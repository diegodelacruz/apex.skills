[CmdletBinding(SupportsShouldProcess)]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$sources = Join-Path $root '.upstreams'
$repos = @{
	'apex-mcp' = 'https://github.com/TechFernandesLTDA/apex-mcp.git'
	'zaimella-skill' = 'https://github.com/jefersonKel/zaimella-skill.git'
	'zaimella-apex-oracle' = 'https://github.com/zaimella/zaimella-apex-oracle.git'
}

if ($PSCmdlet.ShouldProcess($sources, 'create upstream source folder')) { New-Item -ItemType Directory -Path $sources -Force | Out-Null }
foreach ($name in $repos.Keys) {
	$target = Join-Path $sources $name
	if (Test-Path -LiteralPath (Join-Path $target '.git')) { Write-Output "PRESENT repo=$name path=$target"; continue }
	if (Test-Path -LiteralPath $target) { throw "Target exists but is not a Git checkout: $target" }
	if ($PSCmdlet.ShouldProcess($target, "clone $name")) { git clone --depth 1 $repos[$name] $target; Write-Output "CLONED repo=$name revision=$(git -C $target rev-parse HEAD)" }
}
