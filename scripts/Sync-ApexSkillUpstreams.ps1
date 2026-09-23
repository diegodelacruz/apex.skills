[CmdletBinding(SupportsShouldProcess)]
param(
	[switch]$Offline,
	[string]$PythonExecutable,
	[string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RepositoryRoot)
$manifestPath = Join-Path $root 'vendor/upstreams/manifest.json'
$managedRoot = Join-Path $root '.upstreams/managed'
$backupRoot = Join-Path $root '.upstream-backups'
$lockPath = Join-Path $root 'upstreams.lock.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$lock = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$runRoot = Join-Path $root ('.upstreams/.staging/' + $timestamp)
$statePath = Join-Path $root '.upstreams/state.json'
$state = if (Test-Path -LiteralPath $statePath) { Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } else { [pscustomobject]@{ repositories = [pscustomobject]@{} } }
$changedUpdates = [System.Collections.Generic.List[object]]::new()

function Get-FileSha256 {
	param([string]$Path)
	return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TreeSha256 {
	param([string]$Path)
	$base = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	$lines = @(Get-ChildItem -LiteralPath $Path -File -Recurse -Force | Where-Object {
		$_.FullName -notmatch '[\\/]\.git([\\/]|$)' -and
		$_.FullName -notmatch '[\\/](__pycache__|build|dist)([\\/]|$)' -and
		$_.Name -notmatch '\.(pyc|pyo)$' -and $_.FullName -notmatch '\.egg-info([\\/]|$)'
	} | ForEach-Object {
		$relative = $_.FullName.Substring($base.Length).Replace('\', '/')
		$relative + '|' + (Get-FileSha256 $_.FullName)
	} | Sort-Object)
	$bytes = [Text.Encoding]::UTF8.GetBytes(($lines -join "`n"))
	$shaProvider = [Security.Cryptography.SHA256]::Create()
	try { $sha = $shaProvider.ComputeHash($bytes) } finally { $shaProvider.Dispose() }
	return ([BitConverter]::ToString($sha)).Replace('-', '').ToLowerInvariant()
}

function Get-WorktreePatchSha256 {
	param([string]$Path)
	$diff = @(& git -C $Path diff --binary HEAD)
	if ($LASTEXITCODE -ne 0) { throw "Could not inspect local patch in $Path." }
	$text = if ($diff.Count) { ($diff -join "`n") + "`n" } else { '' }
	$bytes = [Text.Encoding]::UTF8.GetBytes($text)
	$shaProvider = [Security.Cryptography.SHA256]::Create()
	try { $sha = $shaProvider.ComputeHash($bytes) } finally { $shaProvider.Dispose() }
	return ([BitConverter]::ToString($sha)).Replace('-', '').ToLowerInvariant()
}

function Invoke-GitChecked {
	param([string]$Path, [string[]]$Arguments)
	$out = & git -C $Path @Arguments 2>&1
	if ($LASTEXITCODE -ne 0) { throw "Git failed: git -C '$Path' $($Arguments -join ' ')`n$($out | Out-String)" }
	return ($out | Out-String).Trim()
}

function Get-RemoteHead {
	param([string]$Url, [string]$Branch)
	$out = & git ls-remote $Url "refs/heads/$Branch" 2>&1
	if ($LASTEXITCODE -ne 0) { throw "Remote unavailable: $($out | Out-String)" }
	$line = @($out | Where-Object { $_ -match '^[0-9a-f]{40}\s+refs/heads/' }) | Select-Object -First 1
	if (-not $line) { throw "Remote branch not found: $Branch" }
	return (($line -split '\s+')[0]).ToLowerInvariant()
}

function Set-RepositoryState {
	param([string]$Name, [string]$Commit, [string]$TreeHash, [string]$Source)
	$state.repositories | Add-Member -NotePropertyName $Name -NotePropertyValue ([pscustomobject]@{ commit = $Commit; tree_sha256 = $TreeHash; source = $Source }) -Force
}

function Test-PathInsideRoot {
	param([string]$Path)
	$full = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	$base = $root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	return $full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase) -and $full -ne $base
}

function Test-PathInsideDirectory {
	param([string]$Path, [string]$Directory)
	$full = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	$base = [IO.Path]::GetFullPath($Directory).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	return $full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)
}

if (-not (Test-Path -LiteralPath $manifestPath) -or -not (Test-Path -LiteralPath $lockPath)) { throw 'Upstream snapshot manifest or lock file is missing.' }
if (-not (Test-PathInsideRoot $runRoot)) { throw "Staging path escaped repository root: $runRoot" }
[IO.Directory]::CreateDirectory($runRoot) | Out-Null
New-Item -ItemType Directory -Path $managedRoot -Force | Out-Null

try {
	foreach ($property in $manifest.repositories.psobject.Properties) {
		$name = $property.Name
		$record = $null
		$entry = $property.Value
		$locked = $lock.repositories.$name
		if (-not $locked -or $locked.kind -ne 'managed' -or $locked.url -ne $entry.url -or $locked.branch -ne $entry.branch -or $entry.commit -notmatch '^[0-9a-f]{40}$') {
			throw "Snapshot and upstream registry disagree for $name."
		}
		$archive = Join-Path $root (Join-Path 'vendor/upstreams' $entry.archive)
		if (-not (Test-PathInsideDirectory $archive (Join-Path $root 'vendor/upstreams'))) { throw "Snapshot archive path escaped vendor/upstreams for $name." }
		if ((Get-FileSha256 $archive) -ne $entry.archive_sha256) { throw "Snapshot hash mismatch for $name; no upstream was changed." }
		$extractRoot = Join-Path $runRoot ($name + '/seed')
		[IO.Directory]::CreateDirectory($extractRoot) | Out-Null
		Expand-Archive -LiteralPath $archive -DestinationPath $extractRoot -Force
		$candidate = Join-Path $extractRoot 'source'
		if (-not (Test-Path -LiteralPath $candidate)) { throw "Snapshot layout is invalid for $name." }
		if ($entry.overlay) {
			$overlay = Join-Path $root (Join-Path 'vendor/upstreams' $entry.overlay)
			if (-not (Test-PathInsideDirectory $overlay (Join-Path $root 'vendor/upstreams'))) { throw "Overlay path escaped vendor/upstreams for $name." }
			if ((Get-FileSha256 $overlay) -ne $entry.overlay_sha256) { throw "Local overlay hash mismatch for $name." }
			$check = & git -C $candidate apply --check $overlay 2>&1
			if ($LASTEXITCODE -ne 0) { throw "Bundled local overlay is invalid for ${name}: $($check | Out-String)" }
			& git -C $candidate apply $overlay
			if ($LASTEXITCODE -ne 0) { throw "Could not apply bundled local overlay for $name." }
		}

		$target = [IO.Path]::GetFullPath((Join-Path $root $entry.path))
		if (-not (Test-PathInsideDirectory $target $managedRoot)) { throw "Managed target path escaped .upstreams/managed for $name." }
		$seedTreeHash = Get-TreeSha256 $candidate
		$existing = Test-Path -LiteralPath $target
		$activeCommit = $entry.commit
		$activeSource = 'bundled'
		$mayUpdate = $true
		if ($existing) {
			$currentTreeHash = Get-TreeSha256 $target
			$hasGitCheckout = Test-Path -LiteralPath (Join-Path $target '.git') -PathType Container
			$untrackedFiles = if ($hasGitCheckout) { Invoke-GitChecked $target @('ls-files', '--others') } else { '' }
			$record = $state.repositories.$name
			if ($record -and $record.protected_local) {
				$mayUpdate = $false
				$activeCommit = $record.commit
				$activeSource = 'existing-local-copy'
				Write-Warning "[$name] La copia está marcada con cambios locales protegidos; no se reemplaza automáticamente."
			} elseif ($record -and $record.tree_sha256 -eq $currentTreeHash) {
				$activeCommit = $record.commit
				$activeSource = $record.source
			} elseif (($currentTreeHash -eq $seedTreeHash) -or ($hasGitCheckout -and -not $untrackedFiles -and (Invoke-GitChecked $target @('rev-parse', 'HEAD')).ToLowerInvariant() -eq $entry.commit -and -not (Invoke-GitChecked $target @('status', '--porcelain')))) {
				$record = [pscustomobject]@{ commit = $entry.commit; tree_sha256 = $seedTreeHash; source = 'bundled' }
				$activeCommit = $entry.commit
			} elseif ($hasGitCheckout -and -not $untrackedFiles -and -not (Invoke-GitChecked $target @('status', '--porcelain'))) {
				$head = (Invoke-GitChecked $target @('rev-parse', 'HEAD')).ToLowerInvariant()
				$origin = Invoke-GitChecked $target @('remote', 'get-url', 'origin')
				$branch = Invoke-GitChecked $target @('branch', '--show-current')
				if ($head -match '^[0-9a-f]{40}$' -and $origin.TrimEnd('/').Replace('.git', '') -eq $entry.url.TrimEnd('/').Replace('.git', '') -and $branch -eq $entry.branch) {
					$record = [pscustomobject]@{ commit = $head; tree_sha256 = $currentTreeHash; source = 'existing-clean-checkout' }
					$activeCommit = $head
					$activeSource = 'existing-clean-checkout'
				} else {
					$mayUpdate = $false
					$activeSource = 'existing-local-copy'
					$record = [pscustomobject]@{ commit = $head; tree_sha256 = $currentTreeHash; source = 'existing-local-copy'; protected_local = $true }
					Write-Warning "[$name] El checkout existente no coincide con su remoto o rama configurados; se conserva."
				}
			} elseif ($entry.overlay -and (Test-Path -LiteralPath (Join-Path $target '.git') -PathType Container)) {
				$head = (Invoke-GitChecked $target @('rev-parse', 'HEAD')).ToLowerInvariant()
				$dirtyText = Invoke-GitChecked $target @('diff', '--name-only', 'HEAD')
				$dirtyFiles = @($dirtyText -split "`r?`n" | Where-Object { $_ })
				$untracked = $untrackedFiles
				$expectedFiles = @($entry.overlay_files | Sort-Object)
				$actualFiles = @($dirtyFiles | Sort-Object)
				$patchHash = Get-WorktreePatchSha256 $target
				if ($head -eq $entry.commit -and -not $untracked -and ($expectedFiles -join "`n") -eq ($actualFiles -join "`n") -and $patchHash -eq $entry.overlay_sha256) {
					$record = [pscustomobject]@{ commit = $entry.commit; tree_sha256 = $currentTreeHash; source = 'bundled-overlay' }
					$activeCommit = $entry.commit
					$activeSource = 'bundled-overlay'
				} else {
					$mayUpdate = $false
					$activeSource = 'existing-local-copy'
					$record = [pscustomobject]@{ commit = $head; tree_sha256 = $currentTreeHash; source = 'existing-local-copy'; protected_local = $true }
					Write-Warning "[$name] Hay cambios locales fuera del overlay incluido; los conservo y omito el reemplazo remoto."
				}
			} else {
				$mayUpdate = $false
				$activeSource = 'existing-local-copy'
				$record = [pscustomobject]@{ commit = $null; tree_sha256 = $currentTreeHash; source = 'existing-local-copy'; protected_local = $true }
				Write-Warning "[$name] Hay archivos locales distintos al snapshot registrado; los conservo y omito el reemplazo remoto."
			}
		}

		$selected = $null
		if (-not $Offline -and $mayUpdate) {
			try {
				$remoteHead = Get-RemoteHead $entry.url $entry.branch
				if ($remoteHead -ne $activeCommit) {
					$clonePath = Join-Path $runRoot ($name + '/remote')
					$clone = & git clone --branch $entry.branch $entry.url $clonePath 2>&1
					if ($LASTEXITCODE -ne 0) { throw "Clone failed: $($clone | Out-String)" }
					$actualHead = (Invoke-GitChecked $clonePath @('rev-parse', 'HEAD')).ToLowerInvariant()
					if ($actualHead -ne $remoteHead) { throw "Remote moved while cloning; ls-remote=$remoteHead clone=$actualHead" }
					$branch = Invoke-GitChecked $clonePath @('branch', '--show-current')
					if ($branch -ne $entry.branch) { throw "Unexpected remote branch: $branch" }
					$ancestor = & git -C $clonePath merge-base --is-ancestor $activeCommit HEAD 2>&1
					if ($LASTEXITCODE -ne 0) { throw "Remote head is not a fast-forward from active commit $activeCommit." }
					if ($entry.overlay) {
						$overlay = Join-Path $root (Join-Path 'vendor/upstreams' $entry.overlay)
						$check = & git -C $clonePath apply --check $overlay 2>&1
						if ($LASTEXITCODE -ne 0) { throw "Local overlay no longer applies: $($check | Out-String)" }
						& git -C $clonePath apply $overlay
						if ($LASTEXITCODE -ne 0) { throw 'Could not apply local overlay to updated source.' }
					}
					$selected = $clonePath
					$activeCommit = $actualHead
					$activeSource = 'remote-updated'
				} else {
					Write-Output "CURRENT kind=managed repo=$name revision=$remoteHead"
				}
			} catch {
				Write-Warning "[$name] No se pudo validar/actualizar el remoto; se conserva la copia local disponible. $($_.Exception.Message)"
				$selected = $null
			}
		}

		if ($name -eq 'apex-mcp' -and $PythonExecutable -and -not $WhatIfPreference) {
			$buildSource = if ($selected) { $selected } elseif ($existing) { $target } else { $candidate }
			$wheelPath = Join-Path $runRoot 'wheels'
			[IO.Directory]::CreateDirectory($wheelPath) | Out-Null
			$buildOutput = & $PythonExecutable -m pip wheel --disable-pip-version-check --no-deps --wheel-dir $wheelPath $buildSource 2>&1
			if ($LASTEXITCODE -ne 0 -and $selected) {
				Write-Warning "[$name] El snapshot remoto no compila; conservo y valido la copia anterior. $($buildOutput | Out-String)"
				$selected = $null
				$activeCommit = if ($record -and $record.commit) { $record.commit } else { $entry.commit }
				$activeSource = if ($existing) { $activeSource } else { 'bundled' }
				$buildSource = if ($existing) { $target } else { $candidate }
				$buildOutput = & $PythonExecutable -m pip wheel --disable-pip-version-check --no-deps --wheel-dir $wheelPath $buildSource 2>&1
			}
			if ($LASTEXITCODE -ne 0) { throw "No bundled or active apex-mcp source builds successfully: $($buildOutput | Out-String)" }
			Write-Output "BUILD_VALIDATED repo=apex-mcp source=$activeSource"
		} elseif ($name -eq 'apex-mcp' -and $PythonExecutable) {
			Write-Output "WhatIf: would build apex-mcp source=$activeSource before activation."
		}

		if (-not $existing) {
			if ($selected) { $sourcePath = $selected; $activeSource = 'remote-updated' } else { $sourcePath = $candidate; $activeCommit = $entry.commit; $activeSource = 'bundled' }
			if ($PSCmdlet.ShouldProcess($target, "install $name from $activeSource")) {
				New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
				try {
					Copy-Item -LiteralPath $sourcePath -Destination $target -Recurse
				} catch {
					$copyFailure = $_
					if (Test-Path -LiteralPath $target) {
						if (-not (Test-PathInsideDirectory $target $managedRoot)) { throw "Partial install path escaped .upstreams/managed; original error: $copyFailure" }
						[IO.Directory]::Delete($target, $true)
					}
					throw $copyFailure
				}
				$changedUpdates.Add([pscustomobject]@{ name = $name; target = $target; backup = $null })
			}
		} elseif ($selected) {
			$backup = Join-Path $backupRoot (Join-Path $timestamp $name)
			if (-not (Test-PathInsideRoot $backup)) { throw "Backup path escaped repository root: $backup" }
			if ($PSCmdlet.ShouldProcess($backup, "backup active $name before update")) {
				New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
				Copy-Item -LiteralPath $target -Destination $backup -Recurse
				if ((Get-TreeSha256 $backup) -ne (Get-TreeSha256 $target)) { throw "Backup verification failed for $name; active copy left untouched." }
				if ($state.repositories.$name) {
					$state.repositories.$name | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $backup '.upstream-state.json') -Encoding utf8
				}
				$swapOld = Join-Path $runRoot ($name + '/old')
				Move-Item -LiteralPath $target -Destination $swapOld
				$updateRecord = [pscustomobject]@{ name = $name; target = $target; backup = $backup }
				$changedUpdates.Add($updateRecord)
				try {
					Copy-Item -LiteralPath $selected -Destination $target -Recurse
				} catch {
					$copyFailure = $_
					try {
						if (Test-Path -LiteralPath $target) {
							$partial = Join-Path $runRoot ($name + '/partial-candidate')
							Move-Item -LiteralPath $target -Destination $partial
						}
						Move-Item -LiteralPath $swapOld -Destination $target
						[void]$changedUpdates.Remove($updateRecord)
					} catch {
						Write-Warning "[$name] No se pudo restaurar desde staging tras una copia parcial; se intentará recuperar desde el backup verificado. $_"
					}
					throw $copyFailure
				}
			}
		}

		if (Test-Path -LiteralPath $target) {
			$treeHash = Get-TreeSha256 $target
			if (-not $existing -and $activeSource -eq 'bundled') { Write-Output "FALLBACK kind=managed repo=$name revision=$activeCommit source=bundled" }
			if ($mayUpdate) {
				Set-RepositoryState $name $activeCommit $treeHash $activeSource
			} else {
				$record.tree_sha256 = $treeHash
				$state.repositories | Add-Member -NotePropertyName $name -NotePropertyValue $record -Force
			}
		}
	}

	if ($PSCmdlet.ShouldProcess($statePath, 'record verified active upstream versions')) {
		$stateTemp = Join-Path $runRoot 'state.json'
		$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $stateTemp -Encoding utf8
		Move-Item -LiteralPath $stateTemp -Destination $statePath -Force
	}
	Write-Output "UPSTREAM_SYNC_COMPLETE backups=$(Join-Path $backupRoot $timestamp) staging=cleaned"
} catch {
	$originalFailure = $_
	foreach ($item in @($changedUpdates.ToArray()) | Sort-Object -Property name -Descending) {
		try {
			$failed = Join-Path $runRoot ($item.name + '/failed')
			if (Test-Path -LiteralPath $item.target) { Move-Item -LiteralPath $item.target -Destination $failed }
			if ($item.backup -and (Test-Path -LiteralPath $item.backup)) {
				$restore = Join-Path $runRoot ($item.name + '/restore')
				Copy-Item -LiteralPath $item.backup -Destination $restore -Recurse
				Move-Item -LiteralPath $restore -Destination $item.target
			}
		} catch {
			Write-Warning "ROLLBACK_FAILED repo=$($item.name): $_"
		}
	}
	throw $originalFailure
} finally {
	$fullRunRoot = [IO.Path]::GetFullPath($runRoot)
	$fullBase = [IO.Path]::GetFullPath((Join-Path $root '.upstreams/.staging')).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
	if ($fullRunRoot.StartsWith($fullBase, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $runRoot)) {
		[IO.Directory]::Delete($fullRunRoot, $true)
	}
}
