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

if (-not (Test-Path -LiteralPath $wrapper) -or -not (Test-Path -LiteralPath $patcher) -or -not (Test-Path -LiteralPath $handshake) -or -not (Test-Path -LiteralPath $skillInstaller)) {
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

$apexMcpPath = Join-Path $skillsRoot '.upstreams\apex-mcp\apex_mcp'
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
Write-Host '      [OK] Direct connection supported; wallet is optional.' -ForegroundColor Green

Write-Host '[3/7] Checking secure TEST profile...'
$profileStatus = & $python $credentials status --environment test 2>&1
if ($LASTEXITCODE -ne 0) {
	if (-not (Test-Path -LiteralPath $envFile)) {
		throw 'TEST profile is missing and no local .env file was found. Add the ignored .env, then run this command again.'
	}
	Invoke-QuietPython @($credentials, 'import-env', '--environment', 'test')
	Invoke-QuietPython @($credentials, 'validate', '--environment', 'test')
}
Write-Host '      [OK] TEST profile ready.' -ForegroundColor Green

Write-Host '[4/7] Validating TEST MCP handshake...'
Invoke-QuietPython @($handshake, '--environment', 'test')
Write-Host '      [OK] TEST MCP initialize response received.' -ForegroundColor Green

Write-Host '[5/7] Installing skills for Codex CLI...'
& $skillInstaller
if ($LASTEXITCODE -ne 0) { throw 'Could not install APEX skills for Codex CLI.' }
Write-Host '      [OK] APEX coordinator and specialist skills are available.' -ForegroundColor Green

Write-Host '[6/7] Checking Codex MCP registration...'
$mcpList = & codex mcp list 2>&1 | Out-String
if ($mcpList -notmatch '(?m)^apex-mcp-test\s') {
	if ($PSCmdlet.ShouldProcess('Codex user configuration', 'register apex-mcp-test')) {
		& codex mcp add apex-mcp-test -- $python $wrapper --environment test | Out-Null
		if ($LASTEXITCODE -ne 0) { throw 'Could not register apex-mcp-test in Codex.' }
	}
}
Write-Host '      [OK] apex-mcp-test available.' -ForegroundColor Green

Write-Host '[7/7] Project readiness...'
Write-Host "      [OK] $project" -ForegroundColor Green
Write-Host ''
Write-Host 'Next: open a NEW Codex Desktop task or Codex CLI session in this project and describe the read-only diagnosis.' -ForegroundColor Yellow
