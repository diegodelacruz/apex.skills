<#
.SYNOPSIS
    Executes a reviewed Oracle/APEX change bundle in two bounded SQLcl phases.
.DESCRIPTION
    Validates change.json, runs and checks preflight separately, then renders
    apply/verify only after its baseline marker was observed.
    Rollback is never automatic because Oracle DDL can commit implicitly.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Bundle,
    [ValidateSet("test", "testing", "prod", "production")]
    [string]$Environment,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
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
        $output = & $env:APEX_SQLCL_PATH "-S" $env:APEX_SQLCL_CONN "@$script" 2>&1 | Out-String
        return [PSCustomObject]@{ ExitCode = $LASTEXITCODE; Output = $output }
    } finally {
        Remove-Item -LiteralPath $script -ErrorAction SilentlyContinue
    }
}

$preflightSql = [System.IO.Path]::GetTempFileName() + ".sql"
$applyVerifySql = [System.IO.Path]::GetTempFileName() + ".sql"
try {
    & $python $renderer $bundlePath --root $repoRoot --phase preflight --render $preflightSql
    if ($LASTEXITCODE -ne 0) { throw "CHANGE_BUNDLE_INVALID" }
    & $python $renderer $bundlePath --root $repoRoot --phase apply --phase verify --render $applyVerifySql
    if ($LASTEXITCODE -ne 0) { throw "CHANGE_BUNDLE_INVALID" }
    if ($DryRun) {
        Write-Host "=== DRY RUN: preflight ==="
        Get-Content -LiteralPath $preflightSql -Raw
        Write-Host "=== DRY RUN: apply/verify (only after baseline match) ==="
        Get-Content -LiteralPath $applyVerifySql -Raw
        exit 0
    }
    $preflight = Invoke-BundleSqlclPhase -SqlFile $preflightSql
    $expectedMarker = "__CHANGE_BASELINE_OK=" + ((Get-Content -LiteralPath $bundlePath -Raw | ConvertFrom-Json).baseline.fingerprint)
    if ($preflight.ExitCode -ne 0 -or -not $preflight.Output.Contains($expectedMarker)) {
        Write-Error "BASELINE_MISMATCH: preflight did not confirm the diagnosed fingerprint; apply was not executed."
        exit 2
    }
    $applyVerify = Invoke-BundleSqlclPhase -SqlFile $applyVerifySql
    if ($applyVerify.ExitCode -ne 0) { exit $applyVerify.ExitCode }
    Write-Host "[OK] Change bundle completed successfully." -ForegroundColor Green
    exit 0
} finally {
    Remove-Item -LiteralPath $preflightSql -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $applyVerifySql -ErrorAction SilentlyContinue
}
