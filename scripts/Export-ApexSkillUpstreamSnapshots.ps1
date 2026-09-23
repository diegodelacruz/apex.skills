[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
	[switch]$AcceptCurrentApexMcpOverlay
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RepositoryRoot)
$lockPath = Join-Path $root 'upstreams.lock.json'
$vendorPath = Join-Path $root 'vendor/upstreams'
$tempRoot = Join-Path $root ('.upstreams/.staging/vendor-export-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$backupPath = Join-Path $root ('.upstream-backups/vendor-export-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
$oldManifestPath = Join-Path $vendorPath 'manifest.json'
$oldManifest = if (Test-Path -LiteralPath $oldManifestPath) { Get-Content -LiteralPath $oldManifestPath -Raw | ConvertFrom-Json } else { $null }

function Invoke-GitChecked {
	param([string]$Path, [string[]]$Arguments)
	$out = & git -C $Path @Arguments 2>&1
	if ($LASTEXITCODE -ne 0) { throw "Git failed in ${Path}: git $($Arguments -join ' ')`n$($out | Out-String)" }
	return ($out | Out-String).Trim()
}

function Get-Hash {
	param([string]$Path)
	return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-PathInside {
	param([string]$Path)
	$full = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	$base = $root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	return $full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)
}

if (-not (Test-PathInside $tempRoot) -or -not (Test-PathInside $backupPath)) { throw 'Snapshot staging or backup path escaped the repository root.' }
[IO.Directory]::CreateDirectory($tempRoot) | Out-Null
$entries = [ordered]@{}
$nextLock = $lock | ConvertTo-Json -Depth 10 | ConvertFrom-Json

try {
	foreach ($property in $lock.repositories.psobject.Properties) {
		$name = $property.Name
		$source = $property.Value
		if ($source.kind -ne 'managed') { continue }
		$checkout = Join-Path $root $source.path
		if (-not (Test-Path -LiteralPath (Join-Path $checkout '.git'))) { throw "Managed checkout is missing: $($source.path)" }
		$origin = Invoke-GitChecked $checkout @('remote', 'get-url', 'origin')
		if ($origin.TrimEnd('/').Replace('.git', '') -ne $source.url.TrimEnd('/').Replace('.git', '')) { throw "Remote URL mismatch for $name." }
		$branch = Invoke-GitChecked $checkout @('branch', '--show-current')
		if ($branch -ne $source.branch) { throw "Branch mismatch for ${name}: $branch" }
		$commit = Invoke-GitChecked $checkout @('rev-parse', 'HEAD').ToLowerInvariant()
		$status = Invoke-GitChecked $checkout @('status', '--porcelain')
		$untracked = Invoke-GitChecked $checkout @('ls-files', '--others', '--exclude-standard')
		if ($untracked) { throw "Untracked files prevent snapshot export for $name." }

		$stage = Join-Path $tempRoot $name
		[IO.Directory]::CreateDirectory($stage) | Out-Null
		$archiveName = "$name.zip"
		$archivePath = Join-Path $stage $archiveName
		& git -C $checkout archive --format=zip --prefix='source/' --output=$archivePath HEAD
		if ($LASTEXITCODE -ne 0) { throw "Could not create source archive for $name." }
		$manifestEntry = [ordered]@{
			path = $source.path
			url = $source.url
			branch = $source.branch
			commit = $commit
			kind = $source.kind
			purpose = $source.purpose
			license = $source.license
			archive = $archiveName
			archive_sha256 = Get-Hash $archivePath
		}
		if ($name -eq 'apex-mcp') {
			$patchName = 'apex-mcp-local-overlay.patch'
			$patchPath = Join-Path $stage $patchName
			$diff = @(& git -C $checkout diff --binary HEAD)
			if ($LASTEXITCODE -ne 0) { throw 'Could not export the apex-mcp local overlay.' }
			$patchText = if ($diff.Count) { ($diff -join "`n") + "`n" } else { '' }
			[IO.File]::WriteAllText($patchPath, $patchText, [Text.UTF8Encoding]::new($false))
			$patchHash = Get-Hash $patchPath
			$oldPatchHash = if ($oldManifest -and $oldManifest.repositories.'apex-mcp') { $oldManifest.repositories.'apex-mcp'.overlay_sha256 } else { $null }
			if ($status -and $patchHash -ne $oldPatchHash -and -not $AcceptCurrentApexMcpOverlay) {
				throw 'The apex-mcp local overlay changed; review it, then pass -AcceptCurrentApexMcpOverlay to update the bundled overlay.'
			}
			$filesText = Invoke-GitChecked $checkout @('diff', '--name-only', 'HEAD')
			$overlayFiles = @($filesText -split "`r?`n" | Where-Object { $_ } | Sort-Object)
			if (-not $status -and $overlayFiles.Count -gt 0) { throw 'Could not reconcile apex-mcp status and overlay.' }
			$manifestEntry.overlay = $patchName
			$manifestEntry.overlay_sha256 = $patchHash
			$manifestEntry.overlay_files = $overlayFiles
			$extractPath = Join-Path $stage 'overlay-check'
			Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath -Force
			$applyCheck = & git -C (Join-Path $extractPath 'source') apply --check $patchPath 2>&1
			if ($LASTEXITCODE -ne 0) { throw "Apex-mcp overlay does not apply to its archived base: $($applyCheck | Out-String)" }
		} elseif ($status) {
			throw "Local modifications are not allowed in managed source $name."
		}
		$entries[$name] = [pscustomobject]$manifestEntry
		$nextLock.repositories.$name.expected_commit = $commit
	}

	$manifest = [pscustomobject]@{ format_version = 1; snapshot_date = (Get-Date -Format 'yyyy-MM-dd'); repositories = [pscustomobject]$entries }
	$manifestPath = Join-Path $tempRoot 'manifest.json'
	$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8
	if ($PSCmdlet.ShouldProcess($vendorPath, 'replace bundled upstream snapshots and update their pinned commits')) {
		New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
		Copy-Item -LiteralPath $lockPath -Destination (Join-Path $backupPath 'upstreams.lock.json') -Force
		$vendorParent = Split-Path -Parent $vendorPath
		$oldVendor = Join-Path $backupPath 'vendor-previous'
		if (Test-Path -LiteralPath $vendorPath) { Move-Item -LiteralPath $vendorPath -Destination $oldVendor }
		try {
			Move-Item -LiteralPath $tempRoot -Destination $vendorPath
			$lockTemp = Join-Path $vendorParent 'upstreams.lock.json.tmp'
			$nextLock | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $lockTemp -Encoding utf8
			Move-Item -LiteralPath $lockTemp -Destination $lockPath -Force
			Write-Output "SNAPSHOTS_EXPORTED backup=$backupPath"
		} catch {
			if (Test-Path -LiteralPath $oldVendor) {
				if (Test-Path -LiteralPath $vendorPath) { Move-Item -LiteralPath $vendorPath -Destination (Join-Path $backupPath 'vendor-failed') }
				Move-Item -LiteralPath $oldVendor -Destination $vendorPath
			}
			Copy-Item -LiteralPath (Join-Path $backupPath 'upstreams.lock.json') -Destination $lockPath -Force
			throw
		}
	}
} finally {
	if ((Test-PathInside $tempRoot) -and (Test-Path -LiteralPath $tempRoot)) {
		[IO.Directory]::Delete([IO.Path]::GetFullPath($tempRoot), $true)
	}
}
