[CmdletBinding(SupportsShouldProcess)]
param([switch]$Rollback, [string]$BackupPath, [switch]$IncludeReferences)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$sources = Join-Path $root '.upstreams'
$lockPath = Join-Path $root 'upstreams.lock.json'
$syncPath = Join-Path $root 'scripts/Sync-ApexSkillUpstreams.ps1'
$restorePath = Join-Path $root 'scripts/Restore-ApexSkillUpstreamBackup.ps1'
$backup = if ($BackupPath) { $BackupPath } else { Join-Path $root ('.upstream-backups\\' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }

if ($Rollback -and -not $BackupPath) { throw 'Rollback requires an existing -BackupPath.' }
if ($Rollback) {
	& $restorePath -BackupPath $BackupPath -WhatIf:$WhatIfPreference
	if (-not $?) { throw 'Managed upstream rollback failed.' }
	if (-not $IncludeReferences) { return }
}

if (-not $Rollback) {
	& $syncPath -WhatIf:$WhatIfPreference
	if (-not $?) { throw 'Managed upstream synchronization failed; current copies were preserved.' }
	if (-not $IncludeReferences) { return }
}

function Invoke-Git {
	param([string]$Path, [string[]]$Arguments)
	$output = & git -C $Path @Arguments 2>&1
	if ($LASTEXITCODE -ne 0) { throw "Git failed in ${Path}: git $($Arguments -join ' ')`n$output" }
	return ($output | Out-String).Trim()
}

function Normalize-Url {
	param([string]$Url)
	return $Url.TrimEnd('/').TrimEnd('.').TrimEnd('/').ToLowerInvariant().Replace('.git', '')
}

function Restore-Backup {
	param([string]$Path, [object[]]$SelectedEntries)
	foreach ($entry in $SelectedEntries) {
		$source = Join-Path $Path $entry.path
		$target = Join-Path $root $entry.path
		if (-not (Test-Path -LiteralPath $source)) { throw "Backup missing repository: $($entry.path)" }
		if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
		New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
		Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
	}
	Copy-Item -LiteralPath (Join-Path $Path 'upstreams.lock.json') -Destination $lockPath -Force
}

if (-not (Test-Path -LiteralPath $lockPath)) { throw "Upstream lock file not found: $lockPath" }
$lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
$selected = @($lock.repositories.psobject.Properties | ForEach-Object { $_.Value } | Where-Object { $_.kind -eq 'reference' })

if ($Rollback) {
	if (-not $BackupPath -or -not (Test-Path -LiteralPath $BackupPath)) { throw 'Rollback requires an existing -BackupPath.' }
	Restore-Backup -Path $BackupPath -SelectedEntries $selected
	Write-Output "ROLLBACK_COMPLETE backup=$BackupPath"
	exit 0
}

# Read-only preflight: no checkout is modified before every selected repository passes.
foreach ($entry in $selected) {
	$target = Join-Path $root $entry.path
	if (-not (Test-Path -LiteralPath (Join-Path $target '.git'))) { throw "Missing Git working copy: $($entry.path)" }
	$remote = Invoke-Git -Path $target -Arguments @('remote', 'get-url', 'origin')
	if ((Normalize-Url $remote) -ne (Normalize-Url $entry.url)) { throw "Remote URL mismatch for $($entry.path): expected $($entry.url), got $remote" }
	$branch = Invoke-Git -Path $target -Arguments @('branch', '--show-current')
	if ($branch -ne $entry.branch) { throw "Branch mismatch for $($entry.path): expected $($entry.branch), got $branch" }
	$status = Invoke-Git -Path $target -Arguments @('status', '--porcelain')
	if ($status) { throw "Local changes prevent safe update of $($entry.path). Commit or preserve them outside the upstream checkout first." }
	$current = Invoke-Git -Path $target -Arguments @('rev-parse', 'HEAD')
	if ($current -ne $entry.expected_commit) { throw "Expected commit mismatch for $($entry.path): lock has $($entry.expected_commit), checkout has $current" }
	$remoteHead = (git ls-remote $entry.url "refs/heads/$($entry.branch)" 2>&1 | Out-String).Trim()
	if ($LASTEXITCODE -ne 0 -or -not $remoteHead) { throw "Remote preflight failed for $($entry.path): $($entry.url) [$($entry.branch)]" }
}

# Backup is created only after all read-only preflight checks pass and before the first mutation.
if ($PSCmdlet.ShouldProcess($backup, 'create and verify upstream backup')) {
	New-Item -ItemType Directory -Path $backup -Force | Out-Null
	foreach ($entry in $selected) {
		$source = Join-Path $root $entry.path
		$destination = Join-Path $backup $entry.path
		New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
		Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
		if (-not (Test-Path -LiteralPath (Join-Path $destination '.git'))) { throw "Backup verification failed for $($entry.path)" }
	}
	Copy-Item -LiteralPath $lockPath -Destination (Join-Path $backup 'upstreams.lock.json') -Force
	if (-not (Test-Path -LiteralPath (Join-Path $backup 'upstreams.lock.json'))) { throw 'Backup verification failed for upstreams.lock.json' }
} else {
	throw 'Backup creation was not approved; no upstream update was performed.'
}

try {
	foreach ($entry in $selected) {
		$target = Join-Path $root $entry.path
		Invoke-Git -Path $target -Arguments @('fetch', '--prune', 'origin', $entry.branch) | Out-Null
		Invoke-Git -Path $target -Arguments @('merge', '--ff-only', "origin/$($entry.branch)") | Out-Null
		$revision = Invoke-Git -Path $target -Arguments @('rev-parse', 'HEAD')
		$remoteRevision = Invoke-Git -Path $target -Arguments @('rev-parse', "origin/$($entry.branch)")
		if ($revision -ne $remoteRevision) { throw "Final commit does not match origin for $($entry.path): local $revision, origin $remoteRevision" }
		if ($revision -notmatch '^[0-9a-f]{40}$') { throw "Invalid final commit for $($entry.path): $revision" }
		$entry.expected_commit = $revision
		Write-Output "UPDATED kind=$($entry.kind) repo=$($entry.path) revision=$revision"
	}
	$lock | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $lockPath -Encoding utf8
	Write-Output "UPDATE_COMPLETE backup=$backup"
} catch {
	$failure = $_
	try {
		Restore-Backup -Path $backup -SelectedEntries $selected
		Write-Error "UPDATE_FAILED_ROLLED_BACK backup=$backup"
	} catch {
		throw "Update failed and automatic rollback also failed. Original: $failure; rollback: $_"
	}
	throw $failure
}

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
