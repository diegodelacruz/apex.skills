function Get-ApexAuditFileMetadata {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($RepositoryRoot).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    ) + [System.IO.Path]::DirectorySeparatorChar
    $comparison = if ($env:OS -eq "Windows_NT") {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    if ($fullPath.StartsWith($rootPath, $comparison)) {
        $source = $fullPath.Substring($rootPath.Length).Replace([System.IO.Path]::DirectorySeparatorChar, "/")
        if ([System.IO.Path]::AltDirectorySeparatorChar -ne [System.IO.Path]::DirectorySeparatorChar) {
            $source = $source.Replace([System.IO.Path]::AltDirectorySeparatorChar, "/")
        }
    } else {
        $source = "external:" + [System.IO.Path]::GetFileName($fullPath)
    }
    return [ordered]@{
        source        = $source
        source_sha256 = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

function Get-ApexAuditTextHash {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return [System.BitConverter]::ToString($algorithm.ComputeHash($bytes)).Replace("-", "").ToLowerInvariant()
    } finally {
        $algorithm.Dispose()
    }
}

function New-ApexAuditEntry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$EventId,
        [Parameter(Mandatory = $true)][ValidateSet("started", "completed")][string]$EventPhase,
        [Parameter(Mandatory = $true)][string]$Environment,
        [Parameter(Mandatory = $true)][string]$Operation,
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$SourceSha256,
        [Parameter(Mandatory = $true)][string]$Result,
        [AllowNull()][Nullable[int]]$ExitCode,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$TimingsMs,
        [System.Collections.IDictionary]$Metadata = @{}
    )

    $entry = [ordered]@{
        timestamp_utc = [DateTimeOffset]::UtcNow.ToString("o")
        event_id      = $EventId
        event_phase   = $EventPhase
        environment   = $Environment
        operation     = $Operation
        source        = $Source
        source_sha256 = $SourceSha256
        result        = $Result
        exit_code     = $ExitCode
        timings_ms    = $TimingsMs
    }
    foreach ($key in $Metadata.Keys) { $entry[$key] = $Metadata[$key] }
    return $entry
}

function Write-ApexAuditEvent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$AuditPath,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Entry
    )

    $fullAuditPath = [System.IO.Path]::GetFullPath($AuditPath)
    $parent = [System.IO.Path]::GetDirectoryName($fullAuditPath)
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $pathHash = Get-ApexAuditTextHash -Text $fullAuditPath.ToLowerInvariant()
    $mutex = [System.Threading.Mutex]::new($false, "ApexSkillsAudit_$pathHash")
    $locked = $false
    $stream = $null
    try {
        try {
            $locked = $mutex.WaitOne(15000)
        } catch [System.Threading.AbandonedMutexException] {
            $locked = $true
        }
        if (-not $locked) { throw "Timed out waiting for the audit file lock." }

        $line = ($Entry | ConvertTo-Json -Depth 20 -Compress) + [Environment]::NewLine
        $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($line)
        $stream = [System.IO.File]::Open(
            $fullAuditPath,
            [System.IO.FileMode]::Append,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::Read
        )
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        if ($null -ne $stream) { $stream.Dispose() }
        if ($locked) { $mutex.ReleaseMutex() }
        $mutex.Dispose()
    }
}
