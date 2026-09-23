<#
.SYNOPSIS
    Installs the Java and SQLcl runtime used only by apex-controlled-mcp.
.DESCRIPTION
    Downloads a per-user Java 21 runtime from Adoptium and Oracle SQLcl from
    the versioned manifest.  Archives are verified before extraction.  Nothing
    is installed system-wide, added to PATH, or committed to Git.
.EXAMPLE
    .\scripts\Install-ApexControlledRuntime.ps1
#>

[CmdletBinding()]
param(
    [string]$RuntimeRoot = (Join-Path $env:LOCALAPPDATA 'ApexSkills\runtimes'),
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $repoRoot 'runtime\sqlcl-runtime.json'

function Get-VerifiedArchive {
    param(
        [Parameter(Mandatory)] [string]$Uri,
        [Parameter(Mandatory)] [string]$Destination,
        [Parameter(Mandatory)] [string]$ExpectedHash,
        [Parameter(Mandatory)] [ValidateSet('SHA1', 'SHA256')] [string]$Algorithm
    )

    Invoke-WebRequest -Uri $Uri -OutFile $Destination
    $actualHash = (Get-FileHash -LiteralPath $Destination -Algorithm $Algorithm).Hash.ToLowerInvariant()
    if ($actualHash -ne $ExpectedHash.ToLowerInvariant()) {
        throw "RUNTIME_INTEGRITY_FAILED: $Algorithm mismatch for $Uri"
    }
}

function Install-ArchiveComponent {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$Uri,
        [Parameter(Mandatory)] [string]$ExpectedHash,
        [Parameter(Mandatory)] [ValidateSet('SHA1', 'SHA256')] [string]$Algorithm,
        [Parameter(Mandatory)] [string]$Destination
    )

    if ((Test-Path -LiteralPath $Destination) -and -not $Force) {
        Write-Host "[OK] $Name already installed: $Destination" -ForegroundColor Green
        return
    }

    $staging = Join-Path $RuntimeRoot ('.stage-' + [guid]::NewGuid().ToString('N'))
    $archive = Join-Path $staging 'runtime.zip'
    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    try {
        Write-Host "[DOWNLOAD] $Name" -ForegroundColor Cyan
        Get-VerifiedArchive -Uri $Uri -Destination $archive -ExpectedHash $ExpectedHash -Algorithm $Algorithm
        $expanded = Join-Path $staging 'expanded'
        Expand-Archive -LiteralPath $archive -DestinationPath $expanded -Force
        $content = Get-ChildItem -LiteralPath $expanded -Force
        $source = if ($content.Count -eq 1 -and $content[0].PSIsContainer) { $content[0].FullName } else { $expanded }
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        Move-Item -LiteralPath $source -Destination $Destination
        Write-Host "[OK] $Name installed: $Destination" -ForegroundColor Green
    } finally {
        if (Test-Path -LiteralPath $staging) {
            Remove-Item -LiteralPath $staging -Recurse -Force
        }
    }
}

if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "RUNTIME_MANIFEST_MISSING: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null

$javaApi = 'https://api.adoptium.net/v3/assets/latest/21/hotspot?architecture=x64&image_type=jdk&os=windows&vendor=eclipse'
$javaAsset = (Invoke-RestMethod -Uri $javaApi)[0].binary.package
if (-not $javaAsset.checksum -or -not $javaAsset.link) {
    throw 'JAVA_RUNTIME_METADATA_INVALID: Adoptium did not return archive and SHA-256 checksum.'
}
$javaRoot = Join-Path $RuntimeRoot 'java\temurin-21'
Install-ArchiveComponent -Name 'Temurin Java 21' -Uri $javaAsset.link -ExpectedHash $javaAsset.checksum `
    -Algorithm SHA256 -Destination $javaRoot

$sqlclRoot = Join-Path $RuntimeRoot (Join-Path 'sqlcl' $manifest.version)
Install-ArchiveComponent -Name "Oracle SQLcl $($manifest.version)" -Uri $manifest.archive_url `
    -ExpectedHash $manifest.checksum -Algorithm $manifest.checksum_algorithm -Destination $sqlclRoot

$javaExe = Join-Path $javaRoot 'bin\java.exe'
$sqlclExe = Join-Path $sqlclRoot 'bin\sql.exe'
if (-not (Test-Path -LiteralPath $javaExe)) { throw "JAVA_RUNTIME_INVALID: $javaExe not found." }
if (-not (Test-Path -LiteralPath $sqlclExe)) { throw "SQLCL_RUNTIME_INVALID: $sqlclExe not found." }

$previousJavaHome = $env:JAVA_HOME
try {
    $env:JAVA_HOME = $javaRoot
    $versionOutput = & $sqlclExe -version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "SQLCL_RUNTIME_INVALID: sql.exe -version failed: $versionOutput" }
} finally {
    $env:JAVA_HOME = $previousJavaHome
}

$state = [ordered]@{
    java_home = $javaRoot
    java_version = ($javaAsset.name -replace '\.zip$', '')
    java_sha256 = $javaAsset.checksum
    sqlcl_path = $sqlclExe
    sqlcl_version = $manifest.version
    sqlcl_checksum_algorithm = $manifest.checksum_algorithm
    sqlcl_checksum = $manifest.checksum
    installed_at_utc = (Get-Date).ToUniversalTime().ToString('o')
}
$statePath = Join-Path $RuntimeRoot 'runtime-state.json'
$state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
Write-Host "READY: runtime verified. State: $statePath" -ForegroundColor Green
