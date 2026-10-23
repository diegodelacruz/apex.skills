<#
.SYNOPSIS
    Executes a reviewed Oracle/APEX change bundle in two bounded SQLcl phases.
.DESCRIPTION
    Validates change.json, runs and checks preflight separately, then renders
    apply/verify only after its baseline marker was observed.
    Requires explicit action/backup decisions. An accepted snapshot executes
    after preflight and before apply; a failed snapshot prevents apply.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Bundle,
    [ValidateSet("test", "testing", "prod", "production")]
    [string]$Environment,
    [switch]$DryRun,
    [switch]$Confirmed,
    [ValidateSet("yes", "no")]
    [string]$BackupChoice
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Write-ApexAuditEvent.ps1")
. (Join-Path $PSScriptRoot "Invoke-SqlclScript.ps1")
if (-not $DryRun) {
	if (-not $Confirmed) { throw "A live bundle requires -Confirmed after the user's explicit action confirmation." }
	if ($BackupChoice -notin @("yes", "no")) { throw "A live bundle requires -BackupChoice yes or no." }
}
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$renderer = Join-Path $PSScriptRoot "change_bundle.py"
$bundlePath = if ([System.IO.Path]::IsPathRooted($Bundle)) {
    [System.IO.Path]::GetFullPath($Bundle)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Bundle))
}

if (-not (Test-Path -LiteralPath $python)) { throw "Python environment not found: $python" }
$repoPrefix = $repoRoot.TrimEnd("\\", "/") + [System.IO.Path]::DirectorySeparatorChar
if (-not $bundlePath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Bundle must be inside the repository checkout: $Bundle"
}
$bundleDocument = Get-Content -LiteralPath $bundlePath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($BackupChoice -eq "no" -and $bundleDocument.artifacts -and
    ($bundleDocument.artifacts.PSObject.Properties.Name -contains "snapshot")) {
    throw "UNEXPECTED_BACKUP_ARTIFACT: backup was declined; remove snapshot from change.json before execution."
}
. (Join-Path $PSScriptRoot "Initialize-OracleConnection.ps1") -Environment $Environment

function Invoke-BundleSqlclPhase {
    param([Parameter(Mandatory = $true)][string]$SqlFile)
    $script = [System.IO.Path]::GetTempFileName() + ".sql"
    try {
        @(
            "SET ECHO ON",
            "SET FEEDBACK ON",
            "SET SERVEROUTPUT ON SIZE UNLIMITED",
            "SET DEFINE OFF",
            "WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK",
            (Get-Content -LiteralPath $SqlFile -Raw -Encoding UTF8),
            "EXIT"
        ) | Set-Content -LiteralPath $script -Encoding UTF8
        $sqlcl = Invoke-SqlclScript -SqlclPath $env:APEX_SQLCL_PATH -Connection $env:APEX_SQLCL_CONN -ScriptPath $script
        return [PSCustomObject]@{ ExitCode = $sqlcl.ExitCode; Output = $sqlcl.StdOut + $sqlcl.StdErr }
    } finally {
        Remove-Item -LiteralPath $script -ErrorAction SilentlyContinue
    }
}

$preflightSql = [System.IO.Path]::GetTempFileName() + ".sql"
$snapshotSql = [System.IO.Path]::GetTempFileName() + ".sql"
$applyVerifySql = [System.IO.Path]::GetTempFileName() + ".sql"
$script:auditStarted = $false
$script:auditCompleted = $false
$routeWatch = $null
$script:routeWatch = $null
try {
    & $python $renderer $bundlePath --root $repoRoot --phase preflight --render $preflightSql
    if ($LASTEXITCODE -ne 0) { throw "CHANGE_BUNDLE_INVALID" }
    & $python $renderer $bundlePath --root $repoRoot --phase apply --phase verify --render $applyVerifySql
    if ($LASTEXITCODE -ne 0) { throw "CHANGE_BUNDLE_INVALID" }
    if ($BackupChoice -eq "yes") {
        & $python $renderer $bundlePath --root $repoRoot --phase snapshot --render $snapshotSql
        if ($LASTEXITCODE -ne 0) { throw "BACKUP_ARTIFACT_REQUIRED: snapshot.sql is required when backup is accepted." }
    }
    if ($DryRun) {
        Write-Host "=== DRY RUN: preflight ==="
        Get-Content -LiteralPath $preflightSql -Raw
        if ($BackupChoice -eq "yes") {
            Write-Host "=== DRY RUN: accepted snapshot (runs before apply) ==="
            Get-Content -LiteralPath $snapshotSql -Raw
        }
        Write-Host "=== DRY RUN: apply/verify (only after baseline match) ==="
        Get-Content -LiteralPath $applyVerifySql -Raw
        exit 0
    }
    $auditPath = Join-Path $repoRoot "control-proyecto\.bitacora.json"
    $auditEnvironment = if ($env:APEX_ENVIRONMENT) { $env:APEX_ENVIRONMENT } else { "not-set" }
    $bundleIdentity = Get-ApexAuditFileMetadata -Path $bundlePath -RepositoryRoot $repoRoot
    $artifactHashes = [ordered]@{}
    foreach ($property in $bundleDocument.artifacts.PSObject.Properties) {
        if ($null -ne $property.Value -and "$($property.Value)".Length -gt 0) {
            $artifactPath = Join-Path $repoRoot ([string]$property.Value)
            $artifactHashes[$property.Name] = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $auditMetadata = [ordered]@{
        confirmed = $true
        backup_choice = $BackupChoice
        bundle_id = $bundleDocument.id
        kind = $bundleDocument.kind
        target = $bundleDocument.target
        baseline_fingerprint = $bundleDocument.baseline.fingerprint
        artifact_sha256 = $artifactHashes
    }
    $eventId = [Guid]::NewGuid().ToString()
    $auditStart = New-ApexAuditEntry -EventId $eventId -EventPhase started `
        -Environment $auditEnvironment -Operation "oracle_apex_change_bundle" `
        -Source $bundleIdentity.source -SourceSha256 $bundleIdentity.source_sha256 `
        -Result "STARTED" -ExitCode $null -TimingsMs ([ordered]@{}) -Metadata $auditMetadata
    try {
        Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditStart
    } catch {
        [Console]::Error.WriteLine("Audit start could not be persisted; no bundle SQL was submitted: $($_.Exception.Message)")
        exit 3
    }
    $script:auditStarted = $true
    $routeWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $script:routeWatch = $routeWatch
    $script:backupAuditResult = if ($BackupChoice -eq "yes") { "NOT_RUN" } else { "NOT_REQUESTED" }
    function Complete-ApexBundleAudit {
        param([string]$Result, [int]$ExitCode)
        $completionMetadata = [ordered]@{}
        foreach ($key in $auditMetadata.Keys) { $completionMetadata[$key] = $auditMetadata[$key] }
        $completionMetadata.backup_result = $script:backupAuditResult
        $auditComplete = New-ApexAuditEntry -EventId $eventId -EventPhase completed `
            -Environment $auditEnvironment -Operation "oracle_apex_change_bundle" `
            -Source $bundleIdentity.source -SourceSha256 $bundleIdentity.source_sha256 `
            -Result $Result -ExitCode $ExitCode `
            -TimingsMs ([ordered]@{ route_total = $routeWatch.ElapsedMilliseconds }) `
            -Metadata $completionMetadata
        try {
            Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditComplete
            $script:auditCompleted = $true
            return $true
        } catch {
            [Console]::Error.WriteLine("Bundle ended with exit code $ExitCode, but its result could not be persisted to the audit log. Do not retry automatically.")
            return $false
        }
    }
    $preflight = Invoke-BundleSqlclPhase -SqlFile $preflightSql
    $expectedMarker = "__CHANGE_BASELINE_OK=" + ((Get-Content -LiteralPath $bundlePath -Raw | ConvertFrom-Json).baseline.fingerprint)
    if ($preflight.ExitCode -ne 0 -or -not $preflight.Output.Contains($expectedMarker)) {
        [Console]::Error.WriteLine("BASELINE_MISMATCH: preflight did not confirm the diagnosed fingerprint; apply was not executed.")
        if (-not (Complete-ApexBundleAudit -Result "BASELINE_MISMATCH" -ExitCode 2)) { exit 3 }
        exit 2
    }
    if ($BackupChoice -eq "yes") {
        $snapshot = Invoke-BundleSqlclPhase -SqlFile $snapshotSql
        if ($snapshot.ExitCode -ne 0) {
            $script:backupAuditResult = "FAILED"
            [Console]::Error.WriteLine("BACKUP_FAILED: snapshot failed; apply was not executed.")
            if (-not (Complete-ApexBundleAudit -Result "BACKUP_FAILED" -ExitCode $snapshot.ExitCode)) { exit 3 }
            exit $snapshot.ExitCode
        }
        $script:backupAuditResult = "SUCCESS"
    }
    $applyVerify = Invoke-BundleSqlclPhase -SqlFile $applyVerifySql
    if ($applyVerify.ExitCode -ne 0) {
        if (-not (Complete-ApexBundleAudit -Result "SQLCL_FAILED" -ExitCode $applyVerify.ExitCode)) { exit 3 }
        exit $applyVerify.ExitCode
    }
    if (-not (Complete-ApexBundleAudit -Result "SUCCESS" -ExitCode 0)) { exit 3 }
    Write-Host "[OK] Change bundle completed successfully." -ForegroundColor Green
    exit 0
} catch {
    if ($script:auditStarted -and -not $script:auditCompleted) {
        $script:backupAuditResult = if ($BackupChoice -eq "yes" -and $script:backupAuditResult -eq "NOT_RUN") { "UNKNOWN" } else { $script:backupAuditResult }
        if (-not (Complete-ApexBundleAudit -Result "PROCESS_FAILED" -ExitCode 1)) { exit 3 }
    }
    throw
} finally {
    if ($null -ne $routeWatch) { $routeWatch.Stop() }
    Remove-Item -LiteralPath $preflightSql -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $snapshotSql -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $applyVerifySql -ErrorAction SilentlyContinue
}
