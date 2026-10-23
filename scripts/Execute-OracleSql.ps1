<#
.SYNOPSIS
    Executes a SQL file or inline SQL against Oracle via SQLcl.
.DESCRIPTION
    Runs SQL through SQLcl using the connection from $env:APEX_SQLCL_CONN.
    Supports: DDL (CREATE, ALTER, DROP), DML (INSERT, UPDATE, DELETE),
    PL/SQL blocks, and queries (SELECT).
    Requires Initialize-OracleConnection.ps1 to have been sourced first.
.PARAMETER SqlFile
    Path to a .sql file to execute.
.PARAMETER Sql
    Inline SQL statement to execute (alternative to SqlFile).
.PARAMETER SqlclPath
    Path to sql.exe (SQLcl). Default: $env:APEX_SQLCL_PATH.
.PARAMETER ShowErrors
    Run SHOW ERRORS after execution (useful for PL/SQL compilation).
.PARAMETER DryRun
    Print the SQL that would be executed without running it.
.PARAMETER ReadOnly
    Restrict execution to one inline or file-based SELECT in a read-only transaction.
.PARAMETER Confirmed
    Declare the user's explicit confirmation for a live mutation.
.PARAMETER BackupChoice
    Explicit yes/no decision. When yes, BackupSqlFile must contain the scoped backup SQL.
.PARAMETER BackupSqlFile
    Backup SQL artifact executed before the requested mutation when BackupChoice is yes.
.EXAMPLE
    .\scripts\Execute-OracleSql.ps1 -SqlFile "diagnostics\check.sql" -ReadOnly
    .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\create_employees.sql" -Confirmed -BackupChoice no
    .\scripts\Execute-OracleSql.ps1 -SqlFile "dml\change.sql" -Confirmed -BackupChoice yes -BackupSqlFile "dml\backup.sql"
#>

param(
    [Parameter(ParameterSetName="File")]
    [string]$SqlFile,

    [Parameter(ParameterSetName="Inline")]
    [string]$Sql,

    [string]$SqlclPath,
    [switch]$ShowErrors,
    [switch]$DryRun,
    [switch]$ReadOnly,
    [switch]$Confirmed,
    [ValidateSet("yes", "no")]
    [string]$BackupChoice,
    [string]$BackupSqlFile
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Write-ApexAuditEvent.ps1")
. (Join-Path $PSScriptRoot "Invoke-SqlclScript.ps1")

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

# Resolve SQL content
if ($SqlFile) {
    if (-not (Test-Path $SqlFile)) {
        Write-Error "SQL file not found: $SqlFile"
        exit 1
    }
    $sqlContent = Get-Content $SqlFile -Raw -Encoding UTF8
    $sourceName = $SqlFile
} elseif ($Sql) {
    $sqlContent = $Sql
    $sourceName = "(inline)"
} else {
    Write-Error "Provide -SqlFile or -Sql."
    exit 1
}

$normalizedSql = $sqlContent.Trim()
if ($ReadOnly) {
    $singleStatement = $normalizedSql.TrimEnd(';').Trim()
    if ($singleStatement -notmatch '(?is)^select\b' -or $singleStatement.Contains(';') -or
        $singleStatement -match '(?i)--|/\*|\*/') {
        Write-Error "-ReadOnly accepts one SELECT statement without comments or SQLcl terminators."
        exit 1
    }
    if ($Confirmed -or $BackupChoice -or $BackupSqlFile) {
        Write-Error "-ReadOnly cannot be combined with mutation confirmation or backup arguments."
        exit 1
    }
} elseif (-not $DryRun) {
    if (-not $Confirmed) {
        Write-Error "A live mutation requires -Confirmed after the user's explicit action confirmation."
        exit 1
    }
    if ($BackupChoice -notin @("yes", "no")) {
        Write-Error "A live mutation requires -BackupChoice yes or no."
        exit 1
    }
    if ($BackupChoice -eq "yes") {
        if (-not $BackupSqlFile -or -not (Test-Path -LiteralPath $BackupSqlFile)) {
            Write-Error "BackupChoice is yes; provide an existing scoped -BackupSqlFile. No mutation was executed."
            exit 1
        }
        if ($SqlFile -and [IO.Path]::GetFullPath($SqlFile) -eq [IO.Path]::GetFullPath($BackupSqlFile)) {
            Write-Error "The backup SQL file must differ from the change SQL file."
            exit 1
        }
        $backupContent = Get-Content -LiteralPath $BackupSqlFile -Raw -Encoding UTF8
    } elseif ($BackupSqlFile) {
        Write-Error "Do not provide -BackupSqlFile when -BackupChoice is no."
        exit 1
    }
}

# Build the full script to send to SQLcl
$scriptLines = @(
    "SET ECHO ON",
    "SET FEEDBACK ON",
    "SET SERVEROUTPUT ON SIZE UNLIMITED",
    "SET DEFINE OFF",
    "WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK",
    ""
)

if ($ReadOnly) { $scriptLines += "SET TRANSACTION READ ONLY;" }
if ($backupContent) {
    $scriptLines += "PROMPT CHANGE_PHASE=backup"
    $scriptLines += $backupContent
}
$scriptLines += "PROMPT CHANGE_PHASE=change"
$scriptLines += $sqlContent

if ($ShowErrors) {
    $scriptLines += ""
    $scriptLines += "SHOW ERRORS"
}

$scriptLines += ""
$scriptLines += "EXIT"

$fullScript = $scriptLines -join "`n"

# Dry run
if ($DryRun) {
    Write-Host "=== DRY RUN ===" -ForegroundColor Yellow
    Write-Host "SQLcl: $SqlclPath"
    Write-Host "Source: $sourceName"
    Write-Host "--- SQL ---"
    Write-Host $fullScript
    Write-Host "--- END ---"
    exit 0
}

# Execute via SQLcl
Write-Host "[EXEC] Source: $sourceName" -ForegroundColor Cyan
Write-Host "[EXEC] SQLcl: $SqlclPath" -ForegroundColor Cyan
Write-Host "[EXEC] Environment: $($env:APEX_ENVIRONMENT)" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot
$auditPath = Join-Path $repoRoot "control-proyecto\.bitacora.json"
$auditEnvironment = if ($env:APEX_ENVIRONMENT) { $env:APEX_ENVIRONMENT } else { "not-set" }
if ($SqlFile) {
    $sourceIdentity = Get-ApexAuditFileMetadata -Path $SqlFile -RepositoryRoot $repoRoot
} else {
    $sourceIdentity = @{
        source = "(inline)"
        source_sha256 = Get-ApexAuditTextHash -Text $sqlContent
    }
}
$auditMetadata = if ($ReadOnly) {
    [ordered]@{ read_only = $true }
} else {
    [ordered]@{ confirmed = $true; backup_choice = $BackupChoice }
}
if (-not $ReadOnly -and $BackupChoice -eq "yes") {
    $backupIdentity = Get-ApexAuditFileMetadata -Path $BackupSqlFile -RepositoryRoot $repoRoot
    $auditMetadata.backup_source = $backupIdentity.source
    $auditMetadata.backup_source_sha256 = $backupIdentity.source_sha256
}
$operation = if ($ReadOnly) { "oracle_readonly_sql" } elseif ($SqlFile) { "oracle_sql_file" } else { "oracle_inline_sql" }
$eventId = [Guid]::NewGuid().ToString()
$auditStart = New-ApexAuditEntry -EventId $eventId -EventPhase started `
    -Environment $auditEnvironment -Operation $operation `
    -Source $sourceIdentity.source -SourceSha256 $sourceIdentity.source_sha256 `
    -Result "STARTED" -ExitCode $null -TimingsMs ([ordered]@{}) -Metadata $auditMetadata
if (-not $ReadOnly) {
    try {
        Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditStart
    } catch {
        [Console]::Error.WriteLine("Audit start could not be persisted; no SQL was submitted: $($_.Exception.Message)")
        exit 3
    }
}

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
        $fullScript | Out-File -FilePath $tempScript -Encoding UTF8
        $sqlclWatch = [System.Diagnostics.Stopwatch]::StartNew()
        $sqlcl = Invoke-SqlclScript -SqlclPath $SqlclPath -Connection $env:APEX_SQLCL_CONN -ScriptPath $tempScript
        $stdout = $sqlcl.StdOut
        $stderr = $sqlcl.StdErr
        $exitCode = $sqlcl.ExitCode
    } catch {
        $executionError = $_
    } finally {
        if ($null -ne $sqlclWatch) { $sqlclWatch.Stop() }
    }
    $routeWatch.Stop()

    $resultCode = if ($null -ne $executionError) { "PROCESS_FAILED" } elseif ($exitCode -eq 0) { "SUCCESS" } else { "SQLCL_FAILED" }
    $completionMetadata = [ordered]@{}
    foreach ($key in $auditMetadata.Keys) { $completionMetadata[$key] = $auditMetadata[$key] }
    if ($BackupChoice -eq "yes") {
        $completionMetadata.backup_result = if ($exitCode -eq 0) { "SUCCESS" } elseif ($stdout -match "CHANGE_PHASE=change") { "SUCCESS" } elseif ($stdout -match "CHANGE_PHASE=backup") { "FAILED" } else { "UNKNOWN" }
    } else {
        $completionMetadata.backup_result = "NOT_REQUESTED"
    }
    if ($executionError) { $completionMetadata.error_type = $executionError.Exception.GetType().FullName }
    $auditComplete = New-ApexAuditEntry -EventId $eventId -EventPhase completed `
        -Environment $auditEnvironment -Operation $operation `
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
        if ($ReadOnly) {
            Write-Warning "Read-only SQL completed, but its audit result could not be persisted: $($_.Exception.Message)"
        } else {
            if ($stdout) { Write-Host $stdout }
            if ($stderr) { Write-Warning $stderr }
            [Console]::Error.WriteLine("SQL execution ended with exit code $exitCode, but its result could not be persisted to the audit log. Do not retry automatically.")
            exit 3
        }
    }

    if ($stdout) { Write-Host $stdout }
    if ($stderr) { Write-Warning $stderr }
    if ($executionError) {
        Write-Error "SQLcl could not be started or completed: $($executionError.Exception.GetType().FullName)" -ErrorAction Continue
        exit 1
    }
    if ($exitCode -ne 0) {
        Write-Error "SQLcl exited with code $exitCode" -ErrorAction Continue
        exit $exitCode
    }

    Write-Host "[OK] Execution completed successfully." -ForegroundColor Green
    exit 0
} finally {
    $routeWatch.Stop()
    if ($tempScript) {
        Remove-Item $tempScript -ErrorAction SilentlyContinue
    }
}
