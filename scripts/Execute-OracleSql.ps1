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
.PARAMETER Connection
    SQLcl connection string. Default: $env:APEX_SQLCL_CONN.
.PARAMETER SqlclPath
    Path to sql.exe (SQLcl). Default: $env:APEX_SQLCL_PATH.
.PARAMETER ShowErrors
    Run SHOW ERRORS after execution (useful for PL/SQL compilation).
.PARAMETER DryRun
    Print the SQL that would be executed without running it.
.EXAMPLE
    .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\create_employees.sql"
    .\scripts\Execute-OracleSql.ps1 -Sql "SELECT user, sys_context('userenv','current_schema') FROM dual"
    .\scripts\Execute-OracleSql.ps1 -SqlFile "pkg_body.sql" -ShowErrors
#>

param(
    [Parameter(ParameterSetName="File")]
    [string]$SqlFile,

    [Parameter(ParameterSetName="Inline")]
    [string]$Sql,

    [string]$Connection,
    [string]$SqlclPath,
    [switch]$ShowErrors,
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

# Build the full script to send to SQLcl
$scriptLines = @(
    "SET ECHO ON",
    "SET FEEDBACK ON",
    "SET SERVEROUTPUT ON SIZE UNLIMITED",
    "SET DEFINE OFF",
    "WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK",
    "",
    $sqlContent
)

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

$tempScript = [System.IO.Path]::GetTempFileName() + ".sql"
try {
    $fullScript | Out-File -FilePath $tempScript -Encoding UTF8

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
        Write-Error "SQLcl exited with code $($process.ExitCode)"
        exit $process.ExitCode
    }

    Write-Host "[OK] Execution completed successfully." -ForegroundColor Green
    exit 0
} finally {
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    Remove-Item "$tempScript.out" -ErrorAction SilentlyContinue
    Remove-Item "$tempScript.err" -ErrorAction SilentlyContinue
}
