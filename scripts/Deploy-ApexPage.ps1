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
.PARAMETER Connection
    SQLcl connection string. Default: $env:APEX_SQLCL_CONN.
.PARAMETER SqlclPath
    Path to sql.exe (SQLcl). Default: $env:APEX_SQLCL_PATH.
.PARAMETER DryRun
    Show what would be deployed without executing.
.EXAMPLE
    .\scripts\Deploy-ApexPage.ps1 -PageFile "apex\f109_page_291.sql" -ApplicationId 109 -Page 291
    .\scripts\Deploy-ApexPage.ps1 -ApplicationId 109 -Page 291 -ApexDir "apex"
#>

param(
    [string]$PageFile,
    [int]$ApplicationId,
    [int]$Page,
    [string]$ApexDir,
    [string]$Connection,
    [string]$SqlclPath,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Resolve SQLcl
if (-not $SqlclPath) { $SqlclPath = $env:APEX_SQLCL_PATH }
if (-not $SqlclPath -or -not (Test-Path $SqlclPath)) {
    Write-Error "SQLcl not found. Run Initialize-OracleConnection.ps1 first or set -SqlclPath."
    exit 1
}

# Resolve connection
if (-not $Connection) { $Connection = $env:APEX_SQLCL_CONN }
if (-not $Connection) {
    Write-Error "No Oracle connection. Run Initialize-OracleConnection.ps1 first or pass -Connection."
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
    exit 0
}

# Execute deployment
Write-Host "[DEPLOY] File: $PageFile" -ForegroundColor Cyan
Write-Host "[DEPLOY] App: $ApplicationId  Page: $Page" -ForegroundColor Cyan
Write-Host "[DEPLOY] Environment: $($env:APEX_ENVIRONMENT)" -ForegroundColor Cyan

$wrapperScript = @"
SET DEFINE OFF
SET SERVEROUTPUT ON SIZE UNLIMITED
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
@$PageFile
EXIT
"@

$tempScript = [System.IO.Path]::GetTempFileName() + ".sql"
try {
    $wrapperScript | Out-File -FilePath $tempScript -Encoding UTF8

    $process = Start-Process -FilePath $SqlclPath `
        -ArgumentList @("-S", $Connection, "@$tempScript") `
        -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput "$tempScript.out" `
        -RedirectStandardError "$tempScript.err"

    $stdout = if (Test-Path "$tempScript.out") { Get-Content "$tempScript.out" -Raw } else { "" }
    $stderr = if (Test-Path "$tempScript.err") { Get-Content "$tempScript.err" -Raw } else { "" }

    if ($stdout) { Write-Host $stdout }
    if ($stderr) { Write-Warning $stderr }

    if ($process.ExitCode -ne 0) {
        Write-Error "APEX page deploy failed with exit code $($process.ExitCode)"
        exit $process.ExitCode
    }

    Write-Host "[OK] Page $Page deployed to application $ApplicationId successfully." -ForegroundColor Green
    exit 0
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    Remove-Item "$tempScript.out" -ErrorAction SilentlyContinue
    Remove-Item "$tempScript.err" -ErrorAction SilentlyContinue
}
