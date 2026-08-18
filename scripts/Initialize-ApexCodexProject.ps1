[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$ProjectPath = (Get-Location).Path,
	[switch]$InstallSharedDependencies
)

$ErrorActionPreference = 'Stop'
$skillsRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $skillsRoot '.venv\Scripts\python.exe'
$wrapper = Join-Path $skillsRoot 'scripts\run_apex_mcp_with_profile.py'
$project = (Resolve-Path -LiteralPath $ProjectPath).Path

if (-not (Test-Path -LiteralPath $wrapper)) {
	throw "Missing secure MCP wrapper: $wrapper"
}

if ($InstallSharedDependencies) {
	if (-not (Test-Path -LiteralPath $python)) {
		if ($PSCmdlet.ShouldProcess((Join-Path $skillsRoot '.venv'), 'create shared Python environment')) {
			py -3 -m venv (Join-Path $skillsRoot '.venv')
		}
	}
	if ($PSCmdlet.ShouldProcess($skillsRoot, 'install shared skills dependencies')) {
		& $python -m pip install --upgrade pip
		& $python -m pip install -r (Join-Path $skillsRoot 'requirements.txt')
	}
}

if (-not (Test-Path -LiteralPath $python)) {
	throw "Shared runtime missing: $python. Run with -InstallSharedDependencies after approving dependency installation."
}

$mcpList = & codex mcp list 2>&1 | Out-String
if ($mcpList -match '(?m)^apex-mcp-test\s') {
	Write-Output 'PRESENT mcp=apex-mcp-test'
} elseif ($PSCmdlet.ShouldProcess('Codex user configuration', 'register apex-mcp-test')) {
	& codex mcp add apex-mcp-test -- $python $wrapper --environment test
	Write-Output 'REGISTERED mcp=apex-mcp-test'
}

Write-Output "READY project=$project"
Write-Output 'NEXT open a new Codex Desktop task in this project and use apex-database-diagnostics for read-only analysis.'
