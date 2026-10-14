<#
.SYNOPSIS
    Deploys an APEX page export SQL file to Oracle via SQLcl.
.DESCRIPTION
    Takes an APEX page export file (containing wwv_flow_imp.import_begin,
    wwv_flow_imp_page.create_page, wwv_flow_imp.import_end) and executes
    it against the target database using SQLcl.
    This is the equivalent of importing a page through APEX SQL Workshop
    or the command-line import utility.
.PARAMETER PageFile
    Path to the APEX page export SQL file (e.g., f109_page_291.sql).
.PARAMETER ApplicationId
    APEX Application ID. Validated against the export file content.
.PARAMETER Page
    Page number. Validated against the export file content.
.PARAMETER ApexDir
    Directory containing APEX export files. Alternative to PageFile —
    the script will look for f{ApplicationId}_page_{Page}.sql in this dir.
.PARAMETER SqlclPath
    Path to sql.exe (SQLcl). Default: $env:APEX_SQLCL_PATH.
.PARAMETER DryRun
    Show what would be deployed without executing.
.PARAMETER Confirmed
    Declare the user's explicit confirmation for this page import.
.PARAMETER BackupChoice
    Explicit yes/no decision. When yes, BackupFile must be a pre-change native export.
.PARAMETER BackupFile
    Existing native export of the current page, obtained before this import.
.EXAMPLE
    .\scripts\Deploy-ApexPage.ps1 -PageFile "apex\f109_page_291.sql" -ApplicationId 109 -Page 291 -Confirmed -BackupChoice no
    .\scripts\Deploy-ApexPage.ps1 -ApplicationId 109 -Page 291 -ApexDir "apex" -Confirmed -BackupChoice no
#>

param(
    [string]$PageFile,
    [int]$ApplicationId,
    [int]$Page,
    [string]$ApexDir,
    [string]$SqlclPath,
    [switch]$DryRun,
    [switch]$Confirmed,
    [ValidateSet("yes", "no")]
    [string]$BackupChoice,
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Write-ApexAuditEvent.ps1")

# Resolve SQLcl
if (-not $SqlclPath) { $SqlclPath = $env:APEX_SQLCL_PATH }
if (-not $SqlclPath -or -not (Test-Path $SqlclPath)) {
    Write-Error "SQLcl not found. Run Initialize-OracleConnection.ps1 first or set -SqlclPath."
    exit 1
}

# Resolve connection
if (-not $env:APEX_SQLCL_CONN) {
    Write-Error "No Oracle connection. Dot-source Initialize-OracleConnection.ps1 after configuring the repository .env."
    exit 1
}

# Resolve page file
if (-not $PageFile -and $ApexDir -and $ApplicationId -and $Page) {
    $PageFile = Join-Path $ApexDir "f${ApplicationId}_page_${Page}.sql"
}

if (-not $PageFile) {
    Write-Error "Provide -PageFile or -ApexDir with -ApplicationId and -Page."
    exit 1
}

if (-not (Test-Path $PageFile)) {
    Write-Error "Page export file not found: $PageFile"
    exit 1
}

# Validate export file content
$content = Get-Content $PageFile -Raw -Encoding UTF8

$hasImportBegin = $content -match "wwv_flow_imp\.import_begin|wwv_flow_api\.import_begin"
$hasCreatePage  = $content -match "wwv_flow_imp_page\.create_page|wwv_flow_page\.create_page|wwv_flow_step\.create_page|create_page"
$hasImportEnd   = $content -match "wwv_flow_imp\.import_end|wwv_flow_api\.import_end"

if (-not $hasImportBegin) {
    Write-Warning "Export file may be missing import_begin block."
}
if (-not $hasCreatePage) {
    Write-Warning "Export file may be missing create_page block."
}
if (-not $hasImportEnd) {
    Write-Warning "Export file may be missing import_end block."
}

if (-not $DryRun) {
    if (-not $Confirmed) {
        Write-Error "A live page import requires -Confirmed after the user's explicit action confirmation."
        exit 1
    }
    if ($BackupChoice -notin @("yes", "no")) {
        Write-Error "A live page import requires -BackupChoice yes or no."
        exit 1
    }
    if ($BackupChoice -eq "yes") {
        if (-not $BackupFile -or -not (Test-Path -LiteralPath $BackupFile)) {
            Write-Error "BackupChoice is yes; provide a pre-change native export with -BackupFile. No import was executed."
            exit 1
        }
        if ([IO.Path]::GetFullPath($BackupFile) -eq [IO.Path]::GetFullPath($PageFile)) {
            Write-Error "The backup export must differ from the export being imported."
            exit 1
        }
        $backupContent = Get-Content -LiteralPath $BackupFile -Raw -Encoding UTF8
        if ($backupContent -notmatch "wwv_flow_imp\.import_begin|wwv_flow_api\.import_begin" -or
            $backupContent -notmatch "wwv_flow_imp_page\.create_page|wwv_flow_page\.create_page|wwv_flow_step\.create_page|create_page" -or
            $backupContent -notmatch "wwv_flow_imp\.import_end|wwv_flow_api\.import_end") {
            Write-Error "BackupFile is not a complete native APEX page export. No import was executed."
            exit 1
        }
        $deploymentAppId = [regex]::Match($content, "(?i)\bp_default_application_id\s*=>\s*(\d+)")
        $backupAppId = [regex]::Match($backupContent, "(?i)\bp_default_application_id\s*=>\s*(\d+)")
        $deploymentCreatePage = [regex]::Match($content, "(?i)\.create_page\s*\(")
        $backupCreatePage = [regex]::Match($backupContent, "(?i)\.create_page\s*\(")
        $deploymentPageId = if ($deploymentCreatePage.Success) {
            [regex]::Match($content.Substring($deploymentCreatePage.Index + $deploymentCreatePage.Length), "(?i)\bp_id\s*=>\s*(\d+)")
        }
        $backupPageId = if ($backupCreatePage.Success) {
            [regex]::Match($backupContent.Substring($backupCreatePage.Index + $backupCreatePage.Length), "(?i)\bp_id\s*=>\s*(\d+)")
        }
        if (-not $deploymentAppId.Success -or -not $backupAppId.Success -or
            -not $deploymentPageId.Success -or -not $backupPageId.Success -or
            $deploymentAppId.Groups[1].Value -ne $backupAppId.Groups[1].Value -or
            $deploymentPageId.Groups[1].Value -ne $backupPageId.Groups[1].Value) {
            Write-Error "BackupFile application/page identity does not match the page export. No import was executed."
            exit 1
        }
    } elseif ($BackupFile) {
        Write-Error "Do not provide -BackupFile when -BackupChoice is no."
        exit 1
    }
}

# Validate ApplicationId and Page against file content if provided
if ($ApplicationId -and $content -match "p_default_application_id\s*=>\s*(\d+)") {
    $fileAppId = [int]$Matches[1]
    if ($fileAppId -ne $ApplicationId) {
        Write-Error "ApplicationId mismatch: parameter=$ApplicationId, file=$fileAppId"
        exit 1
    }
}

if ($Page -and $content -match "p_id\s*=>\s*(\d+)") {
    $filePageId = [int]$Matches[1]
    if ($filePageId -ne $Page) {
        Write-Warning "Page ID in file ($filePageId) differs from parameter ($Page). Proceeding with file content."
    }
}

# Dry run
if ($DryRun) {
    Write-Host "=== DRY RUN ===" -ForegroundColor Yellow
    Write-Host "Page file:      $PageFile"
    Write-Host "Application ID: $ApplicationId"
    Write-Host "Page:           $Page"
    Write-Host "SQLcl:          $SqlclPath"
    Write-Host "import_begin:   $hasImportBegin"
    Write-Host "create_page:    $hasCreatePage"
    Write-Host "import_end:     $hasImportEnd"
    Write-Host "Backup choice:  $BackupChoice"
    if ($BackupFile) { Write-Host "Backup file:    $BackupFile" }
    exit 0
}

# Execute deployment
Write-Host "[DEPLOY] File: $PageFile" -ForegroundColor Cyan
Write-Host "[DEPLOY] App: $ApplicationId  Page: $Page" -ForegroundColor Cyan
Write-Host "[DEPLOY] Environment: $($env:APEX_ENVIRONMENT)" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot
$auditPath = Join-Path $repoRoot "control-proyecto\.bitacora.json"
$auditEnvironment = if ($env:APEX_ENVIRONMENT) { $env:APEX_ENVIRONMENT } else { "not-set" }
$sourceIdentity = Get-ApexAuditFileMetadata -Path $PageFile -RepositoryRoot $repoRoot
$applicationMatch = [regex]::Match($content, "(?i)\bp_default_application_id\s*=>\s*(\d+)")
$createPageMatch = [regex]::Match($content, "(?i)\.create_page\s*\(")
$pageIdMatch = if ($createPageMatch.Success) {
    [regex]::Match($content.Substring($createPageMatch.Index + $createPageMatch.Length), "(?i)\bp_id\s*=>\s*(\d+)")
}
$auditMetadata = [ordered]@{
    confirmed = $true
    backup_choice = $BackupChoice
    application_id = if ($applicationMatch.Success) { $applicationMatch.Groups[1].Value } else { $null }
    page_id = if ($pageIdMatch.Success) { $pageIdMatch.Groups[1].Value } else { $null }
}
if ($BackupChoice -eq "yes") {
    $backupIdentity = Get-ApexAuditFileMetadata -Path $BackupFile -RepositoryRoot $repoRoot
    $auditMetadata.backup_source = $backupIdentity.source
    $auditMetadata.backup_source_sha256 = $backupIdentity.source_sha256
}
$eventId = [Guid]::NewGuid().ToString()
$auditStart = New-ApexAuditEntry -EventId $eventId -EventPhase started `
    -Environment $auditEnvironment -Operation "apex_native_import" `
    -Source $sourceIdentity.source -SourceSha256 $sourceIdentity.source_sha256 `
    -Result "STARTED" -ExitCode $null -TimingsMs ([ordered]@{}) -Metadata $auditMetadata
try {
    Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditStart
} catch {
    [Console]::Error.WriteLine("Audit start could not be persisted; no APEX import was submitted: $($_.Exception.Message)")
    exit 3
}

$wrapperScript = @"
SET DEFINE OFF
SET SERVEROUTPUT ON SIZE UNLIMITED
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
PROMPT CHANGE_PHASE=change
@$PageFile
EXIT
"@

$routeWatch = [System.Diagnostics.Stopwatch]::StartNew()
$executionError = $null
$stdout = ""
$stderr = ""
$exitCode = 1
$sqlclWatch = $null
$tempScript = $null
try {
    try {
        $tempScript = [System.IO.Path]::GetTempFileName() + ".sql"
        $wrapperScript | Out-File -FilePath $tempScript -Encoding UTF8
        $sqlclWatch = [System.Diagnostics.Stopwatch]::StartNew()
        $process = Start-Process -FilePath $SqlclPath `
            -ArgumentList @("-S", $env:APEX_SQLCL_CONN, "@$tempScript") `
            -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput "$tempScript.out" `
            -RedirectStandardError "$tempScript.err"

        $stdout = if (Test-Path "$tempScript.out") { Get-Content "$tempScript.out" -Raw } else { "" }
        $stderr = if (Test-Path "$tempScript.err") { Get-Content "$tempScript.err" -Raw } else { "" }
        $exitCode = $process.ExitCode
    } catch {
        $executionError = $_
    } finally {
        if ($null -ne $sqlclWatch) { $sqlclWatch.Stop() }
    }
    $routeWatch.Stop()

    $resultCode = if ($executionError) { "PROCESS_FAILED" } elseif ($exitCode -eq 0) { "SUCCESS" } else { "SQLCL_FAILED" }
    $completionMetadata = [ordered]@{}
    foreach ($key in $auditMetadata.Keys) { $completionMetadata[$key] = $auditMetadata[$key] }
    $completionMetadata.backup_result = if ($BackupChoice -eq "yes") { "PROVIDED_NATIVE_EXPORT" } else { "NOT_REQUESTED" }
    if ($executionError) { $completionMetadata.error_type = $executionError.Exception.GetType().FullName }
    $auditComplete = New-ApexAuditEntry -EventId $eventId -EventPhase completed `
        -Environment $auditEnvironment -Operation "apex_native_import" `
        -Source $sourceIdentity.source -SourceSha256 $sourceIdentity.source_sha256 `
        -Result $resultCode -ExitCode $exitCode `
        -TimingsMs ([ordered]@{
            route_total = $routeWatch.ElapsedMilliseconds
            sqlcl_process = if ($null -ne $sqlclWatch) { $sqlclWatch.ElapsedMilliseconds } else { 0 }
        }) `
        -Metadata $completionMetadata
    try {
        Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditComplete
    } catch {
        if ($stdout) { Write-Host $stdout }
        if ($stderr) { Write-Warning $stderr }
        [Console]::Error.WriteLine("APEX import ended with exit code $exitCode, but its result could not be persisted to the audit log. Do not retry automatically.")
        exit 3
    }

    if ($stdout) { Write-Host $stdout }
    if ($stderr) { Write-Warning $stderr }
    if ($executionError) {
        Write-Error "SQLcl could not be started or completed: $($executionError.Exception.GetType().FullName)" -ErrorAction Continue
        exit 1
    }
    if ($exitCode -ne 0) {
        Write-Error "APEX page deploy failed with exit code $exitCode" -ErrorAction Continue
        exit $exitCode
    }

    Write-Host "[OK] Page $Page deployed to application $ApplicationId successfully." -ForegroundColor Green
    exit 0
} finally {
    $routeWatch.Stop()
    if ($tempScript) {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        Remove-Item "$tempScript.out" -ErrorAction SilentlyContinue
        Remove-Item "$tempScript.err" -ErrorAction SilentlyContinue
    }
}
