[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$ProjectPath = (Get-Location).Path,
	[switch]$InstallSharedDependencies,
	[switch]$SkipRemoteProbe
)

$ErrorActionPreference = 'Stop'
$skillsRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $skillsRoot '.venv\Scripts\python.exe'
$credentials = Join-Path $skillsRoot 'scripts\manage_apex_credentials.py'
$adapterValidator = Join-Path $skillsRoot 'scripts\validate_apex_mcp_adapter.py'
$skillInstaller = Join-Path $skillsRoot 'scripts\Install-ApexSkillsForCodex.ps1'
$setupScript = Join-Path $skillsRoot 'scripts\Setup-ApexSkills.ps1'
$project = (Resolve-Path -LiteralPath $ProjectPath).Path
$script:actionItems = [System.Collections.Generic.List[string]]::new()

function Find-Sqlcl {
	$vscodePaths = @(
		"$env:USERPROFILE\.vscode\extensions",
		"$env:USERPROFILE\.vscode-insiders\extensions"
	)
	foreach ($base in $vscodePaths) {
		if (Test-Path -LiteralPath $base) {
			$ext = Get-ChildItem -Path $base -Directory -Filter 'oracle.sql-developer-*' |
				Sort-Object Name -Descending | Select-Object -First 1
			if ($ext) {
				$candidate = Join-Path $ext.FullName 'dbtools\sqlcl\bin\sql.exe'
				if (Test-Path -LiteralPath $candidate) { return $candidate }
			}
		}
	}
	try { $standalone = Get-Command sql -ErrorAction Stop } catch { $standalone = $null }
	if ($standalone -and $standalone.Source) { return $standalone.Source }
	try { $standalone = Get-Command sql.exe -ErrorAction Stop } catch { $standalone = $null }
	if ($standalone -and $standalone.Source) { return $standalone.Source }
	return $null
}

function Get-SqlclProbeState {
	param([ValidateSet('test', 'production')][string]$Environment)
	$sqlclPath = Find-Sqlcl
	if (-not $sqlclPath) { return 'SQLCL_NOT_FOUND' }
	$connStr = (& $python $credentials sqlcl-conn --environment $Environment 2>&1 | Out-String).Trim()
	if ($LASTEXITCODE -ne 0 -or $connStr -match '^SQLCL_CONN_FAIL') { return "SQLCL_CONN_SKIP" }
	$tempSql = [System.IO.Path]::GetTempFileName() + '.sql'
	try {
		Set-Content -Path $tempSql -Value "SET HEADING OFF`nSET FEEDBACK OFF`nSET PAGESIZE 0`nSELECT user FROM dual;`nEXIT;" -Encoding utf8
		$output = & $sqlclPath -S $connStr "@$tempSql" 2>&1 | Out-String
		if ($LASTEXITCODE -eq 0 -and $output -match '\S') {
			$userLine = $output -split "`n" | Where-Object { $_.Trim() -match '^\w+$' } | Select-Object -First 1
			$user = if ($userLine) { $userLine.Trim() } else { 'CONNECTED' }
			return "SQLCL_PROBE_PASS user=$user"
		} else {
			return 'SQLCL_PROBE_FAIL'
		}
	} finally {
		if (Test-Path -LiteralPath $tempSql) { Remove-Item -LiteralPath $tempSql -Force -Confirm:$false }
	}
}

function Get-OracleEnvironmentState {
	param([ValidateSet('test', 'production')][string]$Environment)
	$profile = (& $python $credentials status --environment $Environment 2>&1 | Out-String).Trim()
	$connection = 'NOT_PROBED'
	if ($profile -match '^ORACLE_PROFILE_READY\b') {
		if ($SkipRemoteProbe) {
			$connection = 'SKIPPED'
		} else {
			$connection = (& $python $credentials probe --environment $Environment 2>&1 | Out-String).Trim()
		}
	}
	return [PSCustomObject]@{ Profile = $profile; Connection = $connection }
}

function Get-ShortStatus {
	param([string]$Raw)
	if ($Raw -match 'PASS.*user=(\w+)') { return $Matches[1] }
	if ($Raw -match 'PASS.*schema=(\w+)') { return $Matches[1] }
	if ($Raw -match '_READY\b') { return 'OK' }
	if ($Raw -match '_MISSING\b') { return 'MISSING' }
	if ($Raw -match '_INCOMPLETE\b') { return 'INCOMPLETE' }
	if ($Raw -match '_INVALID\b') { return 'INVALID' }
	if ($Raw -match '_FAIL\b') { return 'FAIL' }
	if ($Raw -match 'NOT_FOUND') { return 'NOT FOUND' }
	if ($Raw -match 'CONN_SKIP') { return 'NO CREDS' }
	if ($Raw -match 'SKIPPED') { return 'SKIPPED' }
	if ($Raw -match 'NOT_PROBED') { return 'NOT PROBED' }
	if ($Raw -match 'PREEXISTING') { return 'REGISTERED' }
	if ($Raw -match 'UNSAFE_SURFACE') { return 'EXCLUDED' }
	return $Raw
}

function Get-StatusColor {
	param([string]$Short)
	if ($Short -in @('OK', 'REGISTERED') -or $Short -cmatch '^[A-Z]{3,}$' -and $Short -notin @('MISSING','FAIL','INVALID','INCOMPLETE','SKIPPED','EXCLUDED')) { return 'Green' }
	if ($Short -in @('MISSING', 'FAIL', 'INVALID', 'NOT FOUND')) { return 'Red' }
	if ($Short -in @('SKIPPED', 'NOT PROBED', 'EXCLUDED', 'NO CREDS', 'INCOMPLETE')) { return 'Yellow' }
	return 'Green'
}

function Write-StatusLine {
	param([string]$Label, [string]$TestRaw, [string]$ProdRaw)
	$testShort = Get-ShortStatus $TestRaw
	$prodShort = Get-ShortStatus $ProdRaw
	$testColor = Get-StatusColor $testShort
	$prodColor = Get-StatusColor $prodShort
	$pad = 22 - $Label.Length
	if ($pad -lt 1) { $pad = 1 }
	Write-Host "      $Label$(' ' * $pad)" -NoNewline
	Write-Host $testShort.PadRight(16) -ForegroundColor $testColor -NoNewline
	Write-Host $prodShort -ForegroundColor $prodColor
}

function Add-Remediation {
	param([string]$Component, [string]$Environment, [string]$ShortStatus)
	$env_flag = "--environment $Environment"
	$env_lower = $Environment.ToLower()
	switch ($ShortStatus) {
		'MISSING' {
			switch ($Component) {
				'profile' {
					$script:actionItems.Add("  [$Environment] Perfil Oracle no configurado.")
					$script:actionItems.Add("           Sin esto no se puede conectar a la base de datos de $env_lower.")
					$script:actionItems.Add("           Opcion 1 (desde .env): python scripts/manage_apex_credentials.py import-env $env_flag")
					$script:actionItems.Add("           Opcion 2 (interactivo): python scripts/manage_apex_credentials.py set $env_flag")
					$script:actionItems.Add("")
				}
				'apex' {
					$script:actionItems.Add("  [$Environment] Credenciales APEX App Builder no configuradas.")
					$script:actionItems.Add("           Sin esto no se puede importar/exportar aplicaciones APEX en $env_lower.")
					$script:actionItems.Add("           Se necesita: URL del App Builder, workspace, usuario y password APEX.")
					$script:actionItems.Add("           Opcion 1 (desde .env): python scripts/manage_apex_credentials.py import-env $env_flag")
					$script:actionItems.Add("           Opcion 2 (interactivo): python scripts/manage_apex_credentials.py set-apex $env_flag")
					$script:actionItems.Add("           Variables .env requeridas: APEX_*_BASE_URL, APEX_*_WORKSPACE, APEX_*_USER, APEX_*_PASSWORD")
					$script:actionItems.Add("")
				}
			}
		}
		'INCOMPLETE' {
			switch ($Component) {
				'profile' {
					$script:actionItems.Add("  [$Environment] Perfil Oracle incompleto (faltan campos).")
					$script:actionItems.Add("           Ejecutar de nuevo: python scripts/manage_apex_credentials.py set $env_flag")
					$script:actionItems.Add("")
				}
				'apex' {
					$script:actionItems.Add("  [$Environment] Perfil APEX App Builder incompleto.")
					$script:actionItems.Add("           Ejecutar de nuevo: python scripts/manage_apex_credentials.py set-apex $env_flag")
					$script:actionItems.Add("")
				}
			}
		}
		'INVALID' {
			if ($Component -eq 'profile') {
				$script:actionItems.Add("  [$Environment] Perfil Oracle corrupto en el keyring.")
				$script:actionItems.Add("           Recrear con: python scripts/manage_apex_credentials.py set $env_flag")
				$script:actionItems.Add("")
			}
		}
		'FAIL' {
			switch ($Component) {
				'connection' {
					$script:actionItems.Add("  [$Environment] Conexion Oracle fallo.")
					$script:actionItems.Add("           Verificar: credenciales correctas, base de datos accesible, servicio/SID valido.")
					$script:actionItems.Add("           Para diagnosticar: python scripts/manage_apex_credentials.py probe $env_flag")
					$script:actionItems.Add("")
				}
				'sqlcl' {
					$script:actionItems.Add("  [$Environment] SQLcl no pudo conectarse.")
					$script:actionItems.Add("           Probar manualmente: sql user/pass@host:port/service")
					$script:actionItems.Add("           Si Oracle conecta pero SQLcl no, verificar version de Java y SQLcl.")
					$script:actionItems.Add("")
				}
			}
		}
		'NOT FOUND' {
			if ($Component -eq 'sqlcl') {
				$script:actionItems.Add("  [General] SQLcl no encontrado en el sistema.")
				$script:actionItems.Add("           SQLcl es necesario para ejecutar SQL, DDL y desplegar paginas APEX.")
				$script:actionItems.Add("           Opcion 1: Instalar extension 'Oracle SQL Developer' en VS Code (incluye SQLcl).")
				$script:actionItems.Add("           Opcion 2: Descargar SQLcl de oracle.com y agregar al PATH.")
				$script:actionItems.Add("")
			}
		}
		'NOT PROBED' {
			if ($Component -eq 'connection') {
				$script:actionItems.Add("  [$Environment] Conexion no probada porque el perfil Oracle no esta listo.")
				$script:actionItems.Add("           Primero configurar el perfil: python scripts/manage_apex_credentials.py set $env_flag")
				$script:actionItems.Add("")
			}
		}
	}
}

function Collect-Remediations {
	param([string]$Environment, [string]$ProfileRaw, [string]$ConnRaw, [string]$SqlclRaw, [string]$ApexRaw)
	Add-Remediation 'profile' $Environment (Get-ShortStatus $ProfileRaw)
	Add-Remediation 'connection' $Environment (Get-ShortStatus $ConnRaw)
	Add-Remediation 'sqlcl' $Environment (Get-ShortStatus $SqlclRaw)
	Add-Remediation 'apex' $Environment (Get-ShortStatus $ApexRaw)
}

# ---------- Bootstrap ----------

Write-Host ''
Write-Host 'APEX Codex Bootstrap' -ForegroundColor Cyan
Write-Host '--------------------' -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $adapterValidator) -or -not (Test-Path -LiteralPath $skillInstaller)) {
	throw 'Required local bootstrap scripts are missing.'
}

Write-Host '[0/6] Preparing bundled upstreams, Python dependencies, and skills...'
if ($InstallSharedDependencies) {
	Write-Host '      -InstallSharedDependencies is retained for compatibility; dependency setup now runs automatically.' -ForegroundColor Gray
}
& $setupScript -SkipSkillInstall -WhatIf:$WhatIfPreference
if (-not $?) { throw 'Local skills setup failed. Review the step output above; upstream fallbacks preserve the available copy.' }

# [1/6] Python
Write-Host '[1/6] Python environment...'
if (-not (Test-Path -LiteralPath $python)) { throw 'Setup completed without creating .venv; review the setup output above.' }
Write-Host '      [OK] Python dependencies ready.' -ForegroundColor Green

# [2/6] MCP adapter
Write-Host '[2/6] Upstream MCP adapter...'
$adapterOutput = (& $python $adapterValidator 2>&1 | Out-String).Trim()
$adapterReady = $LASTEXITCODE -eq 0
if ($adapterOutput -match 'MCP_ADAPTER_READY') {
	Write-Host '      [OK] Adapter encontrado y verificado.' -ForegroundColor Green
} else {
	Write-Host '      [!!] Adapter no disponible.' -ForegroundColor Red
	$script:actionItems.Add("  [General] MCP adapter no encontrado.")
	$script:actionItems.Add("           Revisar la salida de Sync-ApexSkillUpstreams.ps1 y Setup-ApexSkills.ps1.")
	$script:actionItems.Add("")
}
if ($adapterOutput -match 'MCP_SURFACE_UNSAFE') {
	Write-Host '      [!]  Superficie restringida (operaciones APEX internas excluidas por seguridad).' -ForegroundColor Yellow
}

# [3/6] Oracle profiles and probes
Write-Host '[3/6] Oracle profiles and probes...'
$testState = Get-OracleEnvironmentState -Environment test
$productionState = Get-OracleEnvironmentState -Environment production
$oracleTest = $testState.Profile
$oracleTestConnection = $testState.Connection
$oracleProduction = $productionState.Profile
$oracleProductionConnection = $productionState.Connection
$apexTest = (& $python $credentials apex-status --environment test 2>&1 | Out-String).Trim()
$apexProduction = (& $python $credentials apex-status --environment production 2>&1 | Out-String).Trim()
$sqlclTestProbe = 'SQLCL_PROBE_SKIPPED'
$sqlclProductionProbe = 'SQLCL_PROBE_SKIPPED'
if ($SkipRemoteProbe) {
	Write-Host '      Probes omitidos por -SkipRemoteProbe.' -ForegroundColor Yellow
} else {
	if ($oracleTestConnection -match '^ORACLE_CONNECTION_PASS\b') {
		$sqlclTestProbe = Get-SqlclProbeState -Environment test
	}
	if ($oracleProductionConnection -match '^ORACLE_CONNECTION_PASS\b') {
		$sqlclProductionProbe = Get-SqlclProbeState -Environment production
	}
}

Write-Host ''
Write-Host '      Componente             TEST            Production' -ForegroundColor Cyan
Write-Host '      ---------------------- --------------- ---------------' -ForegroundColor DarkGray
Write-StatusLine 'Perfil Oracle' $oracleTest $oracleProduction
Write-StatusLine 'Conexion Oracle' $oracleTestConnection $oracleProductionConnection
Write-StatusLine 'SQLcl' $sqlclTestProbe $sqlclProductionProbe
Write-StatusLine 'APEX App Builder' $apexTest $apexProduction
Write-Host ''

Collect-Remediations 'TEST' $oracleTest $oracleTestConnection $sqlclTestProbe $apexTest
Collect-Remediations 'Production' $oracleProduction $oracleProductionConnection $sqlclProductionProbe $apexProduction

# [4/6] Skills
Write-Host '[4/6] Installing agent skills...'
& $skillInstaller -WhatIf:$WhatIfPreference
$skillInstallerSucceeded = $?
if (-not $skillInstallerSucceeded) {
	throw @"
No se pudieron instalar las skills.

Verifique que el directorio skills/ contiene las carpetas de cada skill
y que el instalador tiene permisos de ejecucion.
"@
}
Write-Host '      [OK] Coordinator and specialist skills installed.' -ForegroundColor Green

# [5/6] MCP registration
Write-Host '[5/6] MCP registration...'
$mcpTest = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
$mcpProduction = 'MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE'
if (Get-Command codex -ErrorAction SilentlyContinue) {
	$mcpList = & codex mcp list 2>&1 | Out-String
	if ($mcpList -match '(?m)^apex-mcp-test\s') {
		$mcpTest = 'MCP_REGISTRATION_PREEXISTING_UNVERIFIED'
	}
	if ($mcpList -match '(?m)^apex-mcp-production\s') {
		$mcpProduction = 'MCP_REGISTRATION_PREEXISTING_UNVERIFIED'
	}
} else {
	$script:actionItems.Add("  [General] Codex CLI no encontrado en el sistema.")
	$script:actionItems.Add("           Se necesita para registrar MCP servers.")
	$script:actionItems.Add("           Instalar con: npm install -g @anthropic/codex")
	$script:actionItems.Add("")
}
$mcpTestShort = Get-ShortStatus $mcpTest
$mcpProdShort = Get-ShortStatus $mcpProduction
Write-Host "      TEST: " -NoNewline; Write-Host $mcpTestShort -ForegroundColor (Get-StatusColor $mcpTestShort)
Write-Host "      Production: " -NoNewline; Write-Host $mcpProdShort -ForegroundColor (Get-StatusColor $mcpProdShort)

# [6/6] Readiness
Write-Host '[6/6] Project readiness...'
Write-Host "      [OK] $project" -ForegroundColor Green
Write-Host ''

# Action plan
$realItems = $script:actionItems | Where-Object { $_.Trim() -ne '' }
if ($realItems.Count -gt 0) {
	Write-Host '  Plan de accion:' -ForegroundColor Yellow
	Write-Host '  ---------------' -ForegroundColor Yellow
	foreach ($item in $script:actionItems) {
		if ($item.Trim() -eq '') {
			Write-Host ''
		} elseif ($item -match '^\s+\[') {
			Write-Host $item -ForegroundColor Yellow
		} else {
			Write-Host $item -ForegroundColor DarkGray
		}
	}
} else {
	Write-Host '  Todo configurado. No hay acciones pendientes.' -ForegroundColor Green
	Write-Host ''
}

Write-Host 'Initialized and verified by Diego de la Cruz Sandoval' -ForegroundColor Cyan
