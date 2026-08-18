[CmdletBinding(SupportsShouldProcess)]
param([switch]$Rollback, [string]$BackupPath)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$sources = Join-Path $root '.upstreams'
$backup = if ($BackupPath) { $BackupPath } else { Join-Path $root ('.upstream-backups\\' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
$repos = @('apex-mcp', 'zaimella-skill', 'zaimella-apex-oracle')

if ($Rollback) {
	if (-not $BackupPath -or -not (Test-Path -LiteralPath $BackupPath)) { throw 'Rollback requires an existing -BackupPath.' }
	foreach ($repo in $repos) {
		$source = Join-Path $BackupPath $repo; $target = Join-Path $sources $repo
		if (-not (Test-Path -LiteralPath $source)) { throw "Backup missing repository: $repo" }
		if ($PSCmdlet.ShouldProcess($target, "restore $repo from backup")) { if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }; Copy-Item -LiteralPath $source -Destination $target -Recurse -Force }
	}
	Write-Output "ROLLBACK_COMPLETE backup=$BackupPath"
	exit 0
}

foreach ($repo in $repos) { if (-not (Test-Path -LiteralPath (Join-Path (Join-Path $sources $repo) '.git'))) { throw "Missing Git working copy: $repo" } }
if ($PSCmdlet.ShouldProcess($sources, "backup upstreams to $backup")) { New-Item -ItemType Directory -Path $backup -Force | Out-Null; foreach ($repo in $repos) { Copy-Item -LiteralPath (Join-Path $sources $repo) -Destination $backup -Recurse -Force } }
try {
	foreach ($repo in $repos) {
		$target = Join-Path $sources $repo
		if ($PSCmdlet.ShouldProcess($target, "fast-forward $repo")) { git -C $target fetch --prune origin; git -C $target pull --ff-only; Write-Output "UPDATED repo=$repo revision=$(git -C $target rev-parse HEAD)" }
	}
	Write-Output "UPDATE_COMPLETE backup=$backup"
} catch { Write-Error "Restore with: .\\scripts\\Update-ApexSkillUpstreams-V2.ps1 -Rollback -BackupPath '$backup'"; throw }
