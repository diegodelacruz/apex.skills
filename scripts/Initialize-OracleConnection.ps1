<#
.SYNOPSIS
    Loads the Oracle connection for SQLcl from the repository .env.
.DESCRIPTION
    Sets $env:APEX_SQLCL_CONN with a SQLcl-compatible connection string.
    Reads credentials only from the repository-root .env file.
.PARAMETER Environment
    Target environment: testing or production. If omitted, use DB_ENV from the selected .env file.
.EXAMPLE
    . .\scripts\Initialize-OracleConnection.ps1
    . .\scripts\Initialize-OracleConnection.ps1 -Environment production
#>

param(
    [ValidateSet("test", "testing", "prod", "production")]
    [string]$Environment
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

$EnvFile = Join-Path $repoRoot ".env"

# SQLcl path — prefer VS Code extension (latest), fallback to standalone
$sqlclCandidates = @(
    (Get-ChildItem "$env:USERPROFILE\.vscode\extensions\oracle.sql-developer-*\dbtools\sqlcl\bin\sql.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1),
    (Get-Item (Join-Path $env:USERPROFILE "Downloads\sqldeveloper_17_4\SQL Developer\sqldeveloper\bin\sql.exe") -ErrorAction SilentlyContinue)
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
                $key = $parts[0].Trim()
                $value = $parts[1].Trim()
                if ($value.Length -ge 2 -and $value[0] -eq $value[$value.Length - 1] -and $value[0] -in @("'", '"')) {
                    $quote = [string]$value[0]
                    $value = $value.Substring(1, $value.Length - 2)
                    $value = $value.Replace("\\", "\").Replace("\$quote", $quote)
                } else {
                    $value = ($value -split " #", 2)[0].TrimEnd()
                }
                $envVars[$key] = $value
            }
        }
    }
    Write-Host "[OK] Loaded .env from $EnvFile" -ForegroundColor Green
}

if (-not $Environment) {
    $Environment = $envVars["DB_ENV"]
}

if (-not $Environment) {
    Write-Error "Environment is not selected. Set DB_ENV in .env or pass -Environment testing|production."
    return
}

$Environment = $Environment.Trim().ToLowerInvariant()
if ($Environment -in @("test", "testing")) {
    $Environment = "testing"
} elseif ($Environment -in @("prod", "production")) {
    $Environment = "production"
} else {
    Write-Error "Invalid environment. Use test/testing or prod/production."
    return
}

# Resolve connection parameters
$prefix = if ($Environment -eq "production") { "DB_PRODUCTION" } else { "DB_TESTING" }

function Get-EnvOrFile {
    param([string]$Key)
    if ($envVars.ContainsKey($Key)) { return $envVars[$Key] }
    return $null
}

$user     = Get-EnvOrFile "${prefix}_USER"
$password = Get-EnvOrFile "${prefix}_PASSWORD"
$host_    = Get-EnvOrFile "${prefix}_HOST"
$port     = Get-EnvOrFile "${prefix}_PORT"
$sid      = Get-EnvOrFile "${prefix}_SID"

if (-not $user -or -not $password -or -not $host_ -or -not $port -or -not $sid) {
    Write-Warning "Incomplete connection for $Environment. Set ${prefix}_USER, ${prefix}_PASSWORD, ${prefix}_HOST, ${prefix}_SID in the repository .env."
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
