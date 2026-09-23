[CmdletBinding(SupportsShouldProcess)]
param(
	[Parameter(Mandatory)][string]$BackupPath,
	[string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RepositoryRoot)
$backupRoot = [IO.Path]::GetFullPath($BackupPath)
$allowedBackupRoot = [IO.Path]::GetFullPath((Join-Path $root '.upstream-backups')).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$lock = Get-Content -LiteralPath (Join-Path $root 'upstreams.lock.json') -Raw | ConvertFrom-Json
$stageRoot = Join-Path $root ('.upstreams/.staging/restore-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))

function Get-TreeSha256 {
	param([string]$Path)
	$base = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	$lines = @(Get-ChildItem -LiteralPath $Path -File -Recurse -Force | Where-Object { $_.FullName -notmatch '[\\/]\.git([\\/]|$)' -and $_.Name -notmatch '\.(pyc|pyo)$' } | ForEach-Object {
		$relative = $_.FullName.Substring($base.Length).Replace('\', '/')
		$relative + '|' + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
	} | Sort-Object)
	$bytes = [Text.Encoding]::UTF8.GetBytes(($lines -join "`n"))
	$shaProvider = [Security.Cryptography.SHA256]::Create()
	try { $sha = $shaProvider.ComputeHash($bytes) } finally { $shaProvider.Dispose() }
	return ([BitConverter]::ToString($sha)).Replace('-', '').ToLowerInvariant()
}

if (-not $backupRoot.StartsWith($allowedBackupRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'BackupPath must be inside this repository .upstream-backups directory.' }
if (-not (Test-Path -LiteralPath $backupRoot -PathType Container)) { throw "Backup directory not found: $backupRoot" }
[IO.Directory]::CreateDirectory($stageRoot) | Out-Null
$changed = [System.Collections.Generic.List[object]]::new()

try {
	foreach ($property in $lock.repositories.psobject.Properties) {
		$entry = $property.Value
		if ($entry.kind -ne 'managed') { continue }
		$name = $property.Name
		$source = Join-Path $backupRoot $name
		if (-not (Test-Path -LiteralPath $source -PathType Container)) { $source = Join-Path $backupRoot $entry.path }
		if (-not (Test-Path -LiteralPath $source -PathType Container)) { continue }
		$target = Join-Path $root $entry.path
		$restore = Join-Path $stageRoot $name
		Copy-Item -LiteralPath $source -Destination $restore -Recurse
		$sidecar = Join-Path $restore '.upstream-state.json'
		if ((Get-TreeSha256 $restore) -ne (Get-TreeSha256 $source)) { throw "Backup verification failed for $name." }
		if (Test-Path -LiteralPath $sidecar) { Remove-Item -LiteralPath $sidecar -Force }
		if ($PSCmdlet.ShouldProcess($target, "restore $name from $backupRoot")) {
			$failed = Join-Path $stageRoot ($name + '-current')
			if (Test-Path -LiteralPath $target) { Move-Item -LiteralPath $target -Destination $failed }
			try { Move-Item -LiteralPath $restore -Destination $target }
			catch { if (Test-Path -LiteralPath $failed) { Move-Item -LiteralPath $failed -Destination $target }; throw }
			$stateRecord = Join-Path $source '.upstream-state.json'
			$changed.Add([pscustomobject]@{ name = $name; target = $target; old = $failed; state = $stateRecord })
		}
	}

	$statePath = Join-Path $root '.upstreams/state.json'
	$state = if (Test-Path -LiteralPath $statePath) { Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } else { [pscustomobject]@{ repositories = [pscustomobject]@{} } }
	foreach ($item in $changed) {
		if (Test-Path -LiteralPath $item.state) {
			$state.repositories | Add-Member -NotePropertyName $item.name -NotePropertyValue (Get-Content -LiteralPath $item.state -Raw | ConvertFrom-Json) -Force
		} else {
			$state.repositories.PSObject.Properties.Remove($item.name)
		}
	}
	if ($PSCmdlet.ShouldProcess($statePath, 'write restored upstream state')) {
		$stateTemp = Join-Path $stageRoot 'state.json'
		$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $stateTemp -Encoding utf8
		Move-Item -LiteralPath $stateTemp -Destination $statePath -Force
	}
	Write-Output "ROLLBACK_COMPLETE backup=$backupRoot"
} catch {
	$failure = $_
	foreach ($item in @($changed.ToArray()) | Sort-Object -Property name -Descending) {
		try {
			if (Test-Path -LiteralPath $item.target) { Move-Item -LiteralPath $item.target -Destination (Join-Path $stageRoot ($item.name + '-rollback-failed')) }
			if ($item.old -and (Test-Path -LiteralPath $item.old)) { Move-Item -LiteralPath $item.old -Destination $item.target }
		} catch { Write-Error "ROLLBACK_RESTORE_FAILED repo=$($item.name): $_" }
	}
	throw $failure
} finally {
	$fullStage = [IO.Path]::GetFullPath($stageRoot)
	$baseStage = [IO.Path]::GetFullPath((Join-Path $root '.upstreams/.staging')).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	if ($fullStage.StartsWith($baseStage, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $stageRoot)) { [IO.Directory]::Delete($fullStage, $true) }
}
