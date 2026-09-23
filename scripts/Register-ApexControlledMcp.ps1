<#
.SYNOPSIS
    Registers the controlled SQLcl MCP for the current Codex user.
.DESCRIPTION
    This changes only the current user's Codex MCP configuration.  It does not
    connect to Oracle, modify profiles, or register the unsafe apex-mcp
    upstream.  The server's doctor tool validates its managed runtime at start.
.EXAMPLE
    .\scripts\Register-ApexControlledMcp.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$server = Join-Path $repoRoot 'scripts\apex_controlled_mcp.py'
$codex = Get-Command codex -ErrorAction SilentlyContinue

if (-not (Test-Path -LiteralPath $python)) {
    throw "MCP_REGISTRATION_BLOCKED: Python environment not found: $python"
}
if (-not $codex) {
    throw 'MCP_REGISTRATION_BLOCKED: Codex CLI is not available in PATH.'
}

& $codex.Source mcp add apex-controlled -- $python $server
if ($LASTEXITCODE -ne 0) {
    throw 'MCP_REGISTRATION_FAILED: Codex did not register apex-controlled. Existing registrations were not changed.'
}
Write-Host 'MCP_REGISTERED: apex-controlled. Restart Codex and run doctor before Oracle operations.' -ForegroundColor Green
