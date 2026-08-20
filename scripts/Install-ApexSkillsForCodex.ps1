[CmdletBinding(SupportsShouldProcess)]
param(
	[ValidateSet('Junction', 'Copy')]
	[string]$Mode = 'Junction',
	[switch]$Force
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $repositoryRoot 'skills'
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$targetRoot = Join-Path $codexHome 'skills'

if (-not (Test-Path -LiteralPath $sourceRoot)) {
	throw "Skills directory not found: $sourceRoot"
}

if ($Mode -eq 'Junction' -and (Split-Path -Qualifier $sourceRoot) -ne (Split-Path -Qualifier $targetRoot)) {
	throw 'Junction mode requires source and CODEX_HOME on the same drive. Run again with -Mode Copy.'
}

if ($PSCmdlet.ShouldProcess($targetRoot, 'create Codex skills directory')) {
	New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
}

$skillFolders = Get-ChildItem -LiteralPath $sourceRoot -Directory |
	Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }

foreach ($source in $skillFolders) {
	$target = Join-Path $targetRoot $source.Name
	if (Test-Path -LiteralPath $target) {
		$current = Get-Item -LiteralPath $target -Force
		if ($current.LinkType -and $current.Target -and ((Resolve-Path -LiteralPath $current.Target).Path -eq $source.FullName)) {
			Write-Host "      [OK] $($source.Name) is already linked." -ForegroundColor Green
			continue
		}
		if (-not $Force) {
			throw "Target already exists: $target. Review it, then rerun with -Force to preserve it as a timestamped backup."
		}
		$backup = "$target.backup-$(Get-Date -Format 'yyyyMMddHHmmss')"
		if ($PSCmdlet.ShouldProcess($target, "move existing skill to $backup")) {
			Move-Item -LiteralPath $target -Destination $backup
		}
	}

	if ($Mode -eq 'Junction') {
		if ($PSCmdlet.ShouldProcess($target, "link to $($source.FullName)")) {
			New-Item -ItemType Junction -Path $target -Target $source.FullName | Out-Null
			Write-Host "      [OK] Installed $($source.Name) using Junction." -ForegroundColor Green
		} else {
			Write-Host "      [WHATIF] Would install $($source.Name) using Junction." -ForegroundColor Yellow
		}
	} elseif ($PSCmdlet.ShouldProcess($target, "copy $($source.FullName)")) {
		Copy-Item -LiteralPath $source.FullName -Destination $target -Recurse
		Write-Host "      [OK] Installed $($source.Name) using Copy." -ForegroundColor Green
	} else {
		Write-Host "      [WHATIF] Would install $($source.Name) using Copy." -ForegroundColor Yellow
	}
}
