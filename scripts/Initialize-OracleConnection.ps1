<#
.SYNOPSIS
    Loads the Oracle connection for SQLcl from .env or environment variables.
.DESCRIPTION
    Sets $env:APEX_SQLCL_CONN with a SQLcl-compatible connection string.
    Never stores credentials in this file. Reads from:
      1. .env file in repo root (DB_TESTING_* or DB_PRODUCTION_* variables)
      2. Existing environment variables
      3. Interactive prompt (if neither source available)
.PARAMETER Environment
    Target environment: testing or production. Default: testing.
.PARAMETER EnvFile
    Path to .env file. Default: repo root .env.
.EXAMPLE
    . .\scripts\Initialize-OracleConnection.ps1
    . .\scripts\Initialize-OracleConnection.ps1 -Environment production
#>

param(
    [ValidateSet("testing", "production")]
    [string]$Environment = "testing",

    [string]$EnvFile
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $EnvFile) {
    $EnvFile = Join-Path $repoRoot ".env"
}

# SQLcl path — prefer VS Code extension (latest), fallback to standalone
$sqlclCandidates = @(
    (Get-ChildItem "$env:USERPROFILE\.vscode\extensions\oracle.sql-developer-*\dbtools\sqlcl\bin\sql.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1),
    (Get-Item "D:\Users\ddelacruz\Downloads\sqldeveloper_17_4\SQL Developer\sqldeveloper\bin\sql.exe" -ErrorAction SilentlyContinue)
)
$sqlclPath = ($sqlclCandidates | Where-Object { $_ -ne $null } | Select-Object -First 1).FullName

if ($sqlclPath) {
    $env:APEX_SQLCL_PATH = $sqlclPath
    Write-Host "[OK] SQLcl: $sqlclPath" -ForegroundColor Green
} else {
    Write-Warning "SQLcl not found. Set `$env:APEX_SQLCL_PATH manually."
}

# Load .env if it exists
$envVars = @{}
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line -split "=", 2
            if ($parts.Count -eq 2) {
                $envVars[$parts[0].Trim()] = $parts[1].Trim()
            }
        }
    }
    Write-Host "[OK] Loaded .env from $EnvFile" -ForegroundColor Green
}

# Resolve connection parameters
$prefix = if ($Environment -eq "production") { "DB_PRODUCTION" } else { "DB_TESTING" }

function Get-EnvOrFile {
    param([string]$Key)
    $envVal = [Environment]::GetEnvironmentVariable($Key)
    if ($envVal) { return $envVal }
    if ($envVars.ContainsKey($Key)) { return $envVars[$Key] }
    return $null
}

$user     = Get-EnvOrFile "${prefix}_USER"
$password = Get-EnvOrFile "${prefix}_PASSWORD"
$host_    = Get-EnvOrFile "${prefix}_HOST"
$port     = Get-EnvOrFile "${prefix}_PORT"
$sid      = Get-EnvOrFile "${prefix}_SID"

if (-not $user -or -not $password -or -not $host_ -or -not $sid) {
    Write-Warning "Incomplete connection for $Environment. Set ${prefix}_USER, ${prefix}_PASSWORD, ${prefix}_HOST, ${prefix}_SID in .env or environment."
    Write-Host "Required variables:" -ForegroundColor Yellow
    @("${prefix}_USER", "${prefix}_PASSWORD", "${prefix}_HOST", "${prefix}_PORT", "${prefix}_SID") | ForEach-Object {
        $val = Get-EnvOrFile $_
        $status = if ($val -and $val -notmatch "^replace_with") { "[set]" } else { "[MISSING]" }
        Write-Host "  $_ $status"
    }
    return
}

if ($user -match "^replace_with" -or $password -match "^replace_with") {
    Write-Warning "Connection variables contain placeholder values. Edit .env with real credentials."
    return
}

if (-not $port) { $port = "1521" }

# Build SQLcl connection string: user/password@host:port/service
$env:APEX_SQLCL_CONN = "${user}/${password}@${host_}:${port}/${sid}"
$env:APEX_ENVIRONMENT = $Environment

Write-Host "[OK] Connection configured for environment: $Environment" -ForegroundColor Green
Write-Host "[OK] Target: ${user}@${host_}:${port}/${sid}" -ForegroundColor Green
Write-Host "[OK] Variable: `$env:APEX_SQLCL_CONN" -ForegroundColor Green
