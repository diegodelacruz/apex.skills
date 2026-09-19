[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Junction', 'Copy')]
    [string]$Mode = 'Junction'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$upstreamBootstrap = Join-Path $root 'scripts/Initialize-ApexSkillUpstreams-V2.ps1'
$skillInstaller = Join-Path $root 'scripts/Install-ApexSkillsForCodex.ps1'
$venv = Join-Path $root '.venv'
$python = Join-Path $venv 'Scripts/python.exe'

Write-Host ''
Write-Host 'APEX Skills - clone setup' -ForegroundColor Cyan
Write-Host '=========================' -ForegroundColor Cyan
Write-Host 'This prepares local sources and tools only. It does not access Oracle or store credentials.' -ForegroundColor Gray

Write-Host '[1/3] Preparing managed upstreams...'
& $upstreamBootstrap
if ($LASTEXITCODE -ne 0) { throw 'Upstream bootstrap failed. Check Git/network access and rerun this script.' }

Write-Host '[2/3] Preparing shared Python environment...'
if (-not (Test-Path -LiteralPath $python)) {
    if ($PSCmdlet.ShouldProcess($venv, 'create Python virtual environment')) {
        py -3 -m venv $venv
    }
}
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Python 3 was not found or the virtual environment could not be created.'
}
if ($PSCmdlet.ShouldProcess($root, 'install project dependencies')) {
    & $python -m pip install --disable-pip-version-check --quiet --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'Could not upgrade pip.' }
    & $python -m pip install --disable-pip-version-check --quiet -r (Join-Path $root 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Could not install requirements.txt.' }
    & $python -m pip install --disable-pip-version-check --quiet -e (Join-Path $root '.upstreams/managed/apex-mcp')
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Could not install the local apex-mcp runtime. Confirm upstream access and rerun; base tests do not require this optional runtime.' }
}

Write-Host '[3/3] Installing skills for Codex...'
& $skillInstaller -Mode $Mode
if ($LASTEXITCODE -ne 0) { throw 'Could not install skills for Codex.' }

Write-Host ''
Write-Host '[OK] Clone setup completed.' -ForegroundColor Green
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Yellow
Write-Host '1. REQUIRED: create .env in the repository root from .env.example and fill DB_TESTING_USER, DB_TESTING_PASSWORD, DB_TESTING_HOST, DB_TESTING_PORT, and DB_TESTING_SID.' -ForegroundColor Yellow
Write-Host '   Never commit .env or paste its values into chat.' -ForegroundColor Yellow
Write-Host '2. Import and validate the TEST profile with manage_apex_credentials.py.' -ForegroundColor Yellow
Write-Host '   ./.venv/Scripts/python.exe ./scripts/manage_apex_credentials.py import-env --environment test' -ForegroundColor Yellow
Write-Host '   ./.venv/Scripts/python.exe ./scripts/manage_apex_credentials.py validate --environment test' -ForegroundColor Yellow
Write-Host '3. Run Initialize-ApexCodexProject.ps1 -ProjectPath <RUTA_PROYECTO_APEX> to validate MCP TEST.' -ForegroundColor Yellow
Write-Host '4. If connection fails, use the diagnostic message; no credentials are printed.' -ForegroundColor Yellow
