<#
.SYNOPSIS
    Prepares the standalone controlled SQLcl MCP without managed APEX upstreams.
.DESCRIPTION
    Creates this repository's Python environment, installs its declared Python
    dependencies, and installs the per-user Java/SQLcl runtime.  It does not
    contact Oracle, create a profile, or register an MCP server.
.EXAMPLE
    .\scripts\Setup-ApexControlledMcp.ps1
#>

[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $repoRoot '.venv'
$python = Join-Path $venv 'Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    if ($PSCmdlet.ShouldProcess($venv, 'create Python virtual environment')) {
        py -3 -m venv $venv
    }
}
if (-not (Test-Path -LiteralPath $python)) {
    throw 'MCP_SETUP_BLOCKED: Python 3 could not create the repository virtual environment.'
}
if ($PSCmdlet.ShouldProcess($repoRoot, 'install controlled MCP dependencies')) {
    & $python -m pip install --disable-pip-version-check --quiet -r (Join-Path $repoRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'MCP_SETUP_FAILED: Could not install Python dependencies.' }
}
if ($PSCmdlet.ShouldProcess($repoRoot, 'install verified SQLcl runtime')) {
    & (Join-Path $PSScriptRoot 'Install-ApexControlledRuntime.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'MCP_SETUP_FAILED: Could not install the controlled runtime.' }
}
Write-Host 'MCP_SETUP_READY: Run Register-ApexControlledMcp.ps1 to add the server to Codex.' -ForegroundColor Green
