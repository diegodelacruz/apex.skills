[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$ProjectPath = (Get-Location).Path,
	[switch]$InstallSharedDependencies,
	[switch]$SkipRemoteProbe
)

$ErrorActionPreference = 'Stop'
$skillsRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $skillsRoot '.venv\Scripts\python.exe'
$credentials = Join-Path $skillsRoot 'scripts\manage_apex_credentials.py'
$adapterValidator = Join-Path $skillsRoot 'scripts\validate_apex_mcp_adapter.py'
$skillInstaller = Join-Path $skillsRoot 'scripts\Install-ApexSkillsForCodex.ps1'
$project = (Resolve-Path -LiteralPath $ProjectPath).Path

function Invoke-QuietPython {
	param([string[]]$Arguments)
	& $python @Arguments | Out-Null
	if ($LASTEXITCODE -ne 0) { throw "Python command failed: $($Arguments -join ' ')" }
}

function Get-OracleEnvironmentState {
	param([ValidateSet('test', 'production')][string]$Environment)
	$profile = (& $python $credentials status --environment $Environment 2>&1 | Out-String).Trim()
	$connection = 'NOT_PROBED'
	if ($profile -match '^ORACLE_PROFILE_READY\b') {
		if ($SkipRemoteProbe) {
			Write-Warning "$Environment Oracle probe skipped by -SkipRemoteProbe."
		} else {
			$connection = (& $python $credentials probe --environment $Environment 2>&1 | Out-String).Trim()
			if ($LASTEXITCODE -ne 0) {
				Write-Warning "$Environment Oracle probe did not pass; continuing local bootstrap."
			}
		}
	} else {
		Write-Warning "$Environment Oracle profile is unavailable or invalid; remote probe will not run."
	}
	return [PSCustomObject]@{ Profile = $profile; Connection = $connection }
}

Write-Host ''
Write-Host 'APEX Codex Bootstrap' -ForegroundColor Cyan
Write-Host '--------------------' -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $adapterValidator) -or -not (Test-Path -LiteralPath $skillInstaller)) {
	throw 'Required local bootstrap scripts are missing.'
}

if ($InstallSharedDependencies) {
	Write-Host '[1/6] Preparing shared Python environment...'
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

Write-Host '[2/6] Checking MCP adapter contract and surface (read-only)...'
$adapterStatus = & $python $adapterValidator 2>&1
$adapterReady = $LASTEXITCODE -eq 0
Write-Host "      $adapterStatus"

Write-Host '[3/6] Checking Oracle profiles and performing permitted read-only probes...'
$testState = Get-OracleEnvironmentState -Environment test
$productionState = Get-OracleEnvironmentState -Environment production
$oracleTest = $testState.Profile
$oracleTestConnection = $testState.Connection
$oracleProduction = $productionState.Profile
$oracleProductionConnection = $productionState.Connection
$apexTest = & $python $credentials apex-status --environment test 2>&1
$apexProduction = & $python $credentials apex-status --environment production 2>&1
Write-Host "      TEST Oracle: $oracleTest"
Write-Host "      TEST connection: $oracleTestConnection"
Write-Host "      Production Oracle: $oracleProduction"
Write-Host "      Production connection: $oracleProductionConnection"
Write-Host "      TEST APEX: $apexTest"
Write-Host "      Production APEX: $apexProduction"

Write-Host '[4/6] Installing agent skills...'
& $skillInstaller
$skillInstallerSucceeded = $?
if (-not $skillInstallerSucceeded) { throw 'Could not install APEX skills.' }
Write-Host '      [OK] APEX coordinator and specialist skills are available.' -ForegroundColor Green
Write-Host '[5/6] Checking agent MCP registration...'
if (Get-Command codex -ErrorAction SilentlyContinue) {
	$mcpList = & codex mcp list 2>&1 | Out-String
	if ($mcpList -match '(?m)^apex-mcp-test\s') {
		$mcpTest = 'MCP_REGISTRATION_PREEXISTING_UNVERIFIED'
	} else {
		$mcpTest = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
	}
	if ($mcpList -match '(?m)^apex-mcp-production\s') {
		$mcpProduction = 'MCP_REGISTRATION_PREEXISTING_UNVERIFIED'
	} else {
		$mcpProduction = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
	}
	Write-Host "      TEST: $mcpTest" -ForegroundColor Yellow
	Write-Host "      Production: $mcpProduction" -ForegroundColor Yellow
} else {
	$mcpTest = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
	$mcpProduction = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
	Write-Host "      TEST: $mcpTest" -ForegroundColor Yellow
	Write-Host "      Production: $mcpProduction" -ForegroundColor Yellow
}
Write-Host '[6/6] Project readiness...'
Write-Host "      [OK] $project" -ForegroundColor Green
Write-Host ''
Write-Host '| Ambiente | Perfil Oracle | Conexión Oracle | APEX App Builder | MCP |' -ForegroundColor Cyan
Write-Host "| TEST | $oracleTest | $oracleTestConnection | $apexTest | $mcpTest |"
Write-Host "| Producción | $oracleProduction | $oracleProductionConnection | $apexProduction | $mcpProduction |"
Write-Host 'El upstream completo no se registra: su superficie contiene operaciones APEX internas inseguras.' -ForegroundColor Yellow
Write-Host ''
Write-Host 'Initialized and verified by Diego de la Cruz Sandoval' -ForegroundColor Cyan
