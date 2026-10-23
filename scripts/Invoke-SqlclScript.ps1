<#
.SYNOPSIS
    Runs a SQLcl script file with the connection sent over stdin.
.DESCRIPTION
    Starts SQLcl as "sql -S /nolog" and writes "connect <conn>" followed by
    "@<script>" to its standard input, so the user/password@dsn string never
    appears in the process command line. Same pattern as
    apex_controlled_mcp.sqlcl_result and manage_apex_credentials.py sqlcl-probe.
    A failed connect exits SQLcl with a non-zero code before the script runs.
#>

function Get-SqlclStdinArguments {
    <# Fixed SQLcl argv: the connection is never part of it. #>
    return @("-S", "/nolog")
}

function Get-SqlclStdinInput {
    param(
        [Parameter(Mandatory = $true)][string]$Connection,
        [Parameter(Mandatory = $true)][string]$ScriptPath
    )
    # DEFINE OFF before connect: an "&" in the password must not trigger substitution.
    return (@(
        "SET DEFINE OFF",
        "WHENEVER SQLERROR EXIT FAILURE",
        "connect $Connection",
        "@`"$ScriptPath`"",
        "EXIT",
        ""
    ) -join "`n")
}

function Invoke-SqlclScript {
    param(
        [Parameter(Mandatory = $true)][string]$SqlclPath,
        [Parameter(Mandatory = $true)][string]$Connection,
        [Parameter(Mandatory = $true)][string]$ScriptPath
    )
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $SqlclPath
    $startInfo.Arguments = (Get-SqlclStdinArguments) -join " "
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    # Same decoding Get-Content applied to the former Start-Process redirect files.
    $startInfo.StandardOutputEncoding = [System.Text.Encoding]::Default
    $startInfo.StandardErrorEncoding = [System.Text.Encoding]::Default
    $startInfo.WorkingDirectory = (Get-Location).ProviderPath

    # SQLcl rejects a BOM-prefixed first command, which would silently drop the
    # WHENEVER guard, and on Windows it reads stdin in the ANSI code page
    # (docs/decisiones/20261016-codificacion-utf8-sqlcl.md).
    $inputEncoding = if ($env:OS -eq "Windows_NT") {
        [System.Text.Encoding]::GetEncoding([System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ANSICodePage)
    } else {
        New-Object System.Text.UTF8Encoding($false)
    }
    $previousConsoleEncoding = $null
    if ($startInfo.PSObject.Properties.Name -contains "StandardInputEncoding") {
        $startInfo.StandardInputEncoding = $inputEncoding
    } else {
        # Windows PowerShell 5.1 (.NET Framework) builds the stdin writer from
        # [Console]::InputEncoding and writes its preamble when the process starts.
        $previousConsoleEncoding = [Console]::InputEncoding
        try { [Console]::InputEncoding = $inputEncoding } catch { $previousConsoleEncoding = $null }
        if ([Console]::InputEncoding.GetPreamble().Length -gt 0) {
            throw "SQLCL_STDIN_ENCODING: stdin would start with a byte-order mark; SQLcl was not started."
        }
    }

    try {
        $process = [System.Diagnostics.Process]::Start($startInfo)
    } finally {
        if ($null -ne $previousConsoleEncoding) { [Console]::InputEncoding = $previousConsoleEncoding }
    }
    try {
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        $process.StandardInput.Write((Get-SqlclStdinInput -Connection $Connection -ScriptPath $ScriptPath))
        $process.StandardInput.Close()
        $process.WaitForExit()
        return [PSCustomObject]@{
            ExitCode = $process.ExitCode
            StdOut = $stdoutTask.Result
            StdErr = $stderrTask.Result
        }
    } finally {
        $process.Dispose()
    }
}
