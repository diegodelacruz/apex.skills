[CmdletBinding(SupportsShouldProcess)]
param(
	[switch]$IncludeReferences
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$lockPath = Join-Path $root 'upstreams.lock.json'
$syncPath = Join-Path $root 'scripts/Sync-ApexSkillUpstreams.ps1'

& $syncPath -WhatIf:$WhatIfPreference
if (-not $?) { throw 'Managed upstream synchronization failed; available copies were preserved.' }
if (-not $IncludeReferences) { return }

if (-not (Test-Path -LiteralPath $lockPath)) { throw "Upstream lock file not found: $lockPath" }
$lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
$entries = @($lock.repositories.psobject.Properties | ForEach-Object { $_.Value } | Where-Object { $_.kind -eq 'reference' })

foreach ($entry in $entries) {
	$target = Join-Path $root $entry.path
	$parent = Split-Path -Parent $target
	if ($PSCmdlet.ShouldProcess($parent, 'create upstream category folder')) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
	if (Test-Path -LiteralPath (Join-Path $target '.git')) {
		$remote = git -C $target remote get-url origin
		if ($LASTEXITCODE -ne 0 -or $remote.TrimEnd('/').TrimEnd('.').TrimEnd('/').ToLowerInvariant().Replace('.git', '') -ne $entry.url.TrimEnd('/').TrimEnd('.').TrimEnd('/').ToLowerInvariant().Replace('.git', '')) { throw "Remote URL mismatch for $($entry.path): expected $($entry.url), got $remote" }
		$branch = git -C $target branch --show-current
		if ($LASTEXITCODE -ne 0 -or $branch.Trim() -ne $entry.branch) { throw "Branch mismatch for $($entry.path): expected $($entry.branch), got $branch" }
		$revision = git -C $target rev-parse HEAD
		if ($LASTEXITCODE -ne 0 -or $revision.Trim() -ne $entry.expected_commit) { throw "Revision mismatch for $($entry.path): expected $($entry.expected_commit), got $revision" }
		Write-Output "PRESENT kind=$($entry.kind) repo=$($entry.path) revision=$($revision.Trim())"
		continue
	}
	if (Test-Path -LiteralPath $target) { throw "Target exists but is not a Git checkout: $target" }
	if ($PSCmdlet.ShouldProcess($target, "clone $($entry.url) branch $($entry.branch)")) {
		git clone --depth 1 --branch $entry.branch $entry.url $target
		if ($LASTEXITCODE -ne 0) { throw "Could not clone $($entry.url)" }
		$revision = git -C $target rev-parse HEAD
		if ($LASTEXITCODE -ne 0 -or $revision.Trim() -ne $entry.expected_commit) {
			throw "Initial revision mismatch for $($entry.path): expected $($entry.expected_commit), got $revision"
		}
		Write-Output "CLONED kind=$($entry.kind) repo=$($entry.path) revision=$revision"
	}
}
