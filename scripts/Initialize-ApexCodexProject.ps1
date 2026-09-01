[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$ProjectPath = (Get-Location).Path,
	[switch]$InstallSharedDependencies
)

$ErrorActionPreference = 'Stop'
$skillsRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $skillsRoot '.venv\Scripts\python.exe'
$wrapper = Join-Path $skillsRoot 'scripts\run_apex_mcp_with_profile.py'
$credentials = Join-Path $skillsRoot 'scripts\manage_apex_credentials.py'
$patcher = Join-Path $skillsRoot 'scripts\Apply-ApexMcpDirectConnectionPatch.py'
$compatibilityPatcher = Join-Path $skillsRoot 'scripts\Apply-ApexMcpApex241CompatibilityPatch.py'
$compatibilityValidator = Join-Path $skillsRoot 'scripts\Validate-ApexMcpApex241Compatibility.py'
$handshake = Join-Path $skillsRoot 'scripts\validate_apex_mcp_handshake.py'
$skillInstaller = Join-Path $skillsRoot 'scripts\Install-ApexSkillsForCodex.ps1'
$envFile = Join-Path $skillsRoot '.env'
$project = (Resolve-Path -LiteralPath $ProjectPath).Path

function Invoke-QuietPython {
	param([string[]]$Arguments)
	& $python @Arguments | Out-Null
	if ($LASTEXITCODE -ne 0) { throw "Python command failed: $($Arguments -join ' ')" }
}

Write-Host ''
Write-Host 'APEX Codex Bootstrap' -ForegroundColor Cyan
Write-Host '--------------------' -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $wrapper) -or -not (Test-Path -LiteralPath $patcher) -or -not (Test-Path -LiteralPath $compatibilityPatcher) -or -not (Test-Path -LiteralPath $compatibilityValidator) -or -not (Test-Path -LiteralPath $handshake) -or -not (Test-Path -LiteralPath $skillInstaller)) {
	throw 'Required APEX MCP integration scripts are missing.'
}

if ($InstallSharedDependencies) {
	Write-Host '[1/7] Preparing shared Python environment...'
	if (-not (Test-Path -LiteralPath $python)) {
		if ($PSCmdlet.ShouldProcess((Join-Path $skillsRoot '.venv'), 'create shared Python environment')) {
			py -3 -m venv (Join-Path $skillsRoot '.venv')
		}
	}
	if ($PSCmdlet.ShouldProcess($skillsRoot, 'install shared skills dependencies')) {
		Invoke-QuietPython @('-m', 'pip', 'install', '--disable-pip-version-check', '--quiet', '--upgrade', 'pip')
		Invoke-QuietPython @('-m', 'pip', 'install', '--disable-pip-version-check', '--quiet', '-r', (Join-Path $skillsRoot 'requirements.txt'))
	}
	Write-Host '      [OK] Shared dependencies ready.' -ForegroundColor Green
} elseif (-not (Test-Path -LiteralPath $python)) {
	throw 'Shared runtime missing. Run again with -InstallSharedDependencies.'
}

$apexMcpPath = Join-Path $skillsRoot '.upstreams\managed\apex-mcp\apex_mcp'
if (-not (Test-Path -LiteralPath $apexMcpPath)) {
	throw @"
Managed upstream 'apex-mcp' is missing.

You must first download upstreams by running:
  .\scripts\Initialize-ApexSkillUpstreams-V2.ps1

Then run this script again.
"@
}

Write-Host '[2/7] Applying direct Oracle connection compatibility...'
Invoke-QuietPython @($patcher)
Write-Host '[2b/7] Applying APEX 24.1.3 metadata compatibility...'
Invoke-QuietPython @($compatibilityPatcher)
Invoke-QuietPython @($compatibilityValidator)
Write-Host '      [OK] APEX 24.1.3 compatibility patch ready.' -ForegroundColor Green
Write-Host '      [OK] Direct connection supported; wallet is optional.' -ForegroundColor Green

Write-Host '[3/7] Checking secure TEST profile...'
$profileStatus = & $python $credentials status --environment test 2>&1
if ($LASTEXITCODE -ne 0) {
	if (-not (Test-Path -LiteralPath $envFile)) {
		throw 'TEST credentials are required. Create .env in the apex.skills repository root from .env.example, fill DB_TESTING_USER/PASSWORD/HOST/PORT/SID, then import and validate with manage_apex_credentials.py. The .env remains local and is never committed.'
	}
	try {
		Invoke-QuietPython @($credentials, 'import-env', '--environment', 'test')
		Invoke-QuietPython @($credentials, 'validate', '--environment', 'test')
	} catch {
		throw 'TEST connection failed. Check DB_TESTING_HOST/PORT/SID, VPN or network access, database availability, and TEST credentials in the local .env. The profile was not printed; correct .env and rerun.'
	}
}
Write-Host '      [OK] TEST profile ready.' -ForegroundColor Green

Write-Host '[4/7] Validating TEST MCP handshake...'
try {
	Invoke-QuietPython @($handshake, '--environment', 'test')
} catch {
	throw 'MCP TEST handshake failed. Confirm the TEST profile validates successfully, apex-mcp is reachable, and the direct-connection patch completed; then rerun this initializer.'
}
Write-Host '      [OK] TEST MCP initialize response received.' -ForegroundColor Green

Write-Host '[5/7] Installing agent skills...'
& $skillInstaller
if ($LASTEXITCODE -ne 0) { throw 'Could not install APEX skills.' }
Write-Host '      [OK] APEX coordinator and specialist skills are available.' -ForegroundColor Green
Write-Host '[6/7] Checking agent MCP registration...'
if (Get-Command codex -ErrorAction SilentlyContinue) {
	$mcpList = & codex mcp list 2>&1 | Out-String
	if ($mcpList -notmatch '(?m)^apex-mcp-test\s') {
		if ($PSCmdlet.ShouldProcess('Codex user configuration', 'register apex-mcp-test')) {
			& codex mcp add apex-mcp-test -- $python $wrapper --environment test | Out-Null
			if ($LASTEXITCODE -ne 0) { throw 'Could not register apex-mcp-test in Codex.' }
		}
	}
	Write-Host '      [OK] apex-mcp-test registered in Codex CLI.' -ForegroundColor Green
} else {
	Write-Host '      [OK] MCP ready. Use Claude Code or Codex CLI to connect.' -ForegroundColor Green
}
Write-Host '[7/7] Project readiness...'
Write-Host "      [OK] $project" -ForegroundColor Green
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Yellow
Write-Host '- Codex CLI: open a new task in this project' -ForegroundColor Yellow
Write-Host '- Claude Code: open this project in Claude Code' -ForegroundColor Yellow
Write-Host 'Then describe the read-only diagnosis to get started.' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Initialized and verified by Diego de la Cruz Sandoval' -ForegroundColor Cyan
