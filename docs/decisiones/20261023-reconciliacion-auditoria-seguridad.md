# Decisión: reconciliar la auditoría de seguridad del 2026-10-01 con `main`

- **Fecha:** 2026-10-23
- **Estado:** pendiente de revisión independiente
- **Objetivo y necesidad:** la rama local `claude/repository-audit-012ba6` (commits `33a8f46`, `3a7b960`, `d6a14a6`, nunca publicada) contenía la auditoría del 2026-10-01 y remediaciones C1–C3 y V1–V4. Desde entonces `main` reemplazó el keyring por el `.env` de la raíz, reescribió el hook de bitácora en JSON Lines y añadió el MCP controlado, por lo que la rama ya no se puede fusionar sin conflictos ni deshacer esos cambios. Hay que decidir, con evidencia, qué hallazgos siguen vigentes y trasladar solo esas correcciones.
- **Alcance:** `scripts/manage_apex_credentials.py`, `scripts/Initialize-ApexCodexProject.ps1`, `scripts/external_repo_indexer.py`, sus pruebas y este registro. No se importan `AUDIT-REPORT*.md`, `PROMPT-CORRECCION-DOCUMENTAL.md` ni `.KNOWN-VULNERABILITIES.md`; no se cambian `CLAUDE.md`, el hook, credenciales ni datos. La rama original se conserva.

## Clasificación de hallazgos

| Hallazgo | Estado en `main` (2026-10-23) | Evidencia |
|---|---|---|
| C1 inyección en `.hooks/pre-commit.sh` | Corregido en `main` | El heredoc es `<<'PYTHON_EOF'` (sin expansión de Bash) y los valores se leen con `subprocess` desde Git. La corrección de la rama (`json.loads(json.dumps("$AUTHOR"))`) no era efectiva: Bash expande la variable antes de que Python la vea. |
| C2 contraseña impresa por `sqlcl-conn` | **Trasladado aquí** | `sqlcl_conn()` imprimía `usuario/contraseña@dsn`; el inicializador la pasaba además como argumento de `sql.exe`. La corrección de la rama (redactar) rompía la sonda SQLcl. |
| C3 `except:` silencioso en el hook | Corregido en `main` | El hook ya no lee ni reescribe la bitácora: agrega una línea JSON con `fsync`. |
| A1 permisos de `.bitacora.json` | Abierto, bajo | `open(..., "a")` hereda la umask en POSIX; el archivo es local, ignorado por Git y contiene autor, rama y rutas. No se modifica aquí. |
| A2 rutas en la bitácora | Obsoleto por diseño | Registrar `files_changed` es el propósito del registro local documentado en `CLAUDE.md`. |
| A3 keyring sin reintentos | Obsoleto | `main` ya no usa keyring; `connect_with_retry` cubre el driver Oracle. |
| A4 conexión sin cierre en `validate_apex_mcp_direct_connection.py` | Abierto, sin impacto de seguridad | El cierre no está en `finally`, pero el proceso termina inmediatamente. Fuera de alcance. |
| M1 marcas de tiempo duplicadas | Corregido en `main` | Cada evento lleva `event_id` UUID4. |
| M2 / D1 orden `3.5` duplicado | Decidido en `main` | `CLAUDE.md` conserva el duplicado hasta verificar consumidores externos. |
| M3 skills en desarrollo invocables | Corregido en `main` | `skills/apex/references/routing.md` y los `SKILL.md` las etiquetan como prototipo. |
| M4 `except Exception` en credenciales | Obsoleto | El código de keyring fue eliminado. |
| D2–D8 documentación de `CLAUDE.md` | Corregido en `main` | 15 hooks, jerarquía de 4 niveles, entrada retirada, 509 pruebas / 57.94 %, etiquetas de desarrollo, bitácora local ignorada e inventario de `docs/`. |
| Cobertura 16.27 % y `SECURITY.md` ausente | Corregido en `main` | Piso de 55 % en `.coveragerc`; `SECURITY.md` existe en la raíz. |
| L1–L3 informativos | Sin acción | Los documentos y `Sync-ApexSkillUpstreams.ps1` existen; `.mcp.json` local es intencional. |
| Rutas, timeouts y servicios fijos | Abierto, sin impacto de seguridad | Mejora de configuración, fuera de alcance; el servicio de keyring es obsoleto. |
| V1 `--output` fuera del directorio actual en `mine_export_patterns.py` | Descartado | La ruta la elige quien ejecuta la CLI con sus propios permisos; restringirla al directorio actual rompería usos legítimos sin cruzar una frontera de confianza. |
| V2 / V4 recorrido de rutas con el identificador | **Trasladado aquí, ampliado** | `--repo-id ../x` en `learn_external_repo.py delete` borraba `../x.json`. La rama solo protegía `save` y `delete`; ahora `save`, `get`, `exists` y `delete` usan un único validador que además rechaza `C:` y el nombre del índice. |
| V3 mensajes de Oracle en `execute_oracle_ddl` | Descartado | Contradice el contrato vigente de reportar la respuesta de Oracle a la sesión autenticada que la produjo; la propia corrección registraba el mensaje completo con `logging`. |
| V5 hosts internos en `.env.example` | Abierto, bajo | `zaitestdb.zaimella.com` y `sistemas.zaimella.com` siguen en un repositorio público. Cambiarlos es una decisión de la persona usuaria. |

Hallazgo relacionado, nuevo: `Deploy-ApexPage.ps1`, `Execute-OracleSql.ps1` e
`Invoke-OracleApexChange.ps1` pasan `$env:APEX_SQLCL_CONN` (con contraseña) como
argumento de SQLcl, visible en la lista de procesos. Queda abierto como
seguimiento; requiere migrar esas rutas a credenciales por stdin.

## Decisión

1. `sqlcl-conn` informa `SQLCL_CONN_READY` con usuario y DSN, nunca la contraseña.
2. Nueva acción `sqlcl-probe --sqlcl-path <sql.exe>`: ejecuta `sql -S /nolog`, envía `connect` por stdin (como `apex_controlled_mcp.sqlcl_result`) y devuelve `SQLCL_PROBE_PASS user=...`, `SQLCL_PROBE_FAIL error=ORA-nnnnn` o `SQLCL_CONN_SKIP`.
3. `Initialize-ApexCodexProject.ps1` usa `sqlcl-probe`; la contraseña ya no pasa por PowerShell, la línea de comandos ni archivos temporales.
4. `ExternalRepoIndexer` valida todo identificador antes de construir la ruta.

- **Alternativas:** fusionar la rama, descartado por conflictos y regresiones sobre `main`; redactar solo la salida, descartado porque deja la sonda sin credenciales; eliminar la sonda SQLcl, descartado porque es la única comprobación del runtime SQLcl en el bootstrap.
- **Permisos y datos:** solo lee el perfil de `.env` ya usado por `probe`; la consulta es `select user from dual`.
- **Compatibilidad:** la salida de `sqlcl-conn` cambia de formato; su único consumidor era el inicializador. Identificadores generados por el escáner (`github-*`, `local-*`) siguen siendo válidos. Windows y POSIX.
- **Validación:** `tests/test_manage_apex_credentials.py`, `tests/test_manage_apex_credentials_cli.py`, `tests/test_external_context_learn.py` y `scripts/run_ci_checks.py`. La sonda contra SQLcl real queda pendiente de ejecutarse con el `.env` local.
- **Rollback:** revertir el commit; no hay datos ni configuración que restaurar.
- **Descontinuación:** cuando las rutas `APEX_SQLCL_CONN` migren a stdin, revisar si `sqlcl-conn` sigue siendo necesario.
