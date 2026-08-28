#!/usr/bin/env bash
# Bootstrap managed upstream repositories required by apex.skills.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANAGED_DIR="$ROOT/.upstreams/managed"

declare -A REPOS=(
  [apex-mcp]="https://github.com/TechFernandesLTDA/apex-mcp.git"
  [zaimella-skill]="https://github.com/jefersonKel/zaimella-skill.git"
  [zaimella-apex-oracle]="https://github.com/zaimella/zaimella-apex-oracle.git"
)

mkdir -p "$MANAGED_DIR"

for name in "${!REPOS[@]}"; do
  target="$MANAGED_DIR/$name"
  if [[ -d "$target/.git" ]]; then
    echo "[OK] $name already present"
  elif [[ -e "$target" ]]; then
    echo "ERROR: target exists but is not a Git checkout: $target" >&2
    exit 1
  else
    echo "[CLONE] $name"
    git clone --depth 1 "${REPOS[$name]}" "$target"
  fi
done

echo "[OK] Managed upstreams ready under $MANAGED_DIR"
