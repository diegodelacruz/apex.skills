# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3 y objetos Oracle relacionados.

La calidad del repositorio se mide con la [Matriz de calidad interagentes](docs/MATRIZ-CALIDAD-INTERAGENTES.md) y el auditor reproducible `python .\scripts\audit_quality_score.py`; un `FAIL` bloquea la publicación.

**Inventario actual:** 31 skills (25 técnicas + 6 orquestadores), verificadas por el auditor.

**Para developers:** Consulte [CLAUDE.md](CLAUDE.md) — estructura del repositorio, configuración, y desarrollo.

**Para usuarios:** Empiece por [docs/MANUAL-DE-USO.md](docs/MANUAL-DE-USO.md). Describa el objetivo en lenguaje natural: el coordinador detecta el contexto Oracle/APEX y elige las skills especializadas necesarias; no debe escribir `usa apex`.

**Para agregar una skill:** siga la [guía canónica de creación](docs/GUIA-CREAR-NUEVA-SKILL.md) antes de crear el directorio o actualizar los catálogos.

**Configuración por agente:**
- **Para Claude Code**: Consulte [Configuración de Claude Code](docs/setup-claude-code.md) — MCP automático, multi-entorno, interfaz gráfica
- **Para Codex CLI**: Consulte [uso de skills desde terminal](docs/uso-skills-codex-cli.md) — invocación manual desde terminal, almacenamiento en usuario Codex

## Preparación inicial

Después de clonar el repositorio, ejecute un único comando:

    .\scripts\Setup-ApexSkills.ps1

Este comando prepara upstreams, Python y skills. No configura credenciales ni accede a Oracle. Use -Mode Copy si Codex está en otra unidad.

El setup parte de los snapshots incluidos en `vendor/upstreams/`, comprueba
actualizaciones remotas por repositorio y guarda un backup verificable antes de
activar una versión nueva. Un remoto no disponible no bloquea la instalación:
se conserva la copia activa o se usa el snapshot empaquetado. Para inicializar
un proyecto Codex y mostrar su matriz de preparación en la misma ejecución:

    .\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"

Ese comando prepara primero Python, upstreams y skills; después realiza las
sondas Oracle de solo lectura configuradas. Use `-SkipRemoteProbe` para evitar
esas sondas.

El bootstrap local no registra el upstream completo `apex-mcp`: su superficie
contiene rutas APEX internas inseguras. La validación remota TEST requiere
autorización explícita y no convierte ese upstream en un MCP registrable.

Para una instalación Oracle/APEX autocontenida y registrable en Codex, use el
[MCP controlado con SQLcl](docs/MCP-CONTROLADO-SQLCL.md). Administra Java y
SQLcl por usuario, sin depender de VS Code, y conserva los permisos efectivos
de la cuenta Oracle. La guía incluye el flujo para nuevos usuarios, la
validación automática en TEST y la solicitud reutilizable al DBA.

## Principios

- Perfiles TEST/Producción seguros por usuario; sin secretos en Git o documentación.
- Validación de acceso en lectura antes de operar un ambiente.
- Alineación TEST/Producción para páginas existentes y control de rangos por proyecto.
- Cambios a Producción sólo con aprobación explícita separada.
- Gobierno DATA, decisiones, planes, validación SQL y auditoría antes del cierre.

Consulte [dependencias](docs/dependencias.md), [casos de uso](docs/casos-de-uso-apex.md) y [auditoría obligatoria](docs/auditoria-obligatoria.md).

## Infrastructure Scripts

The following scripts support development infrastructure and do not require automated test coverage:

| Script | Purpose | Status |
|--------|---------|--------|
| validate-config.py | Configuration file validation | Active |
| run_apex_mcp_with_profile.py | Runner del upstream completo; sin registro automático por superficie insegura | Blocked |
| apex_controlled_mcp.py | MCP STDIO propio sobre SQLcl administrado | Active |
| Setup-ApexControlledMcp.ps1 | Setup autónomo de Python, Java y SQLcl | Active |
| Register-ApexControlledMcp.ps1 | Registro del MCP propio en Codex | Manual |
| validate_apex_controlled_mcp_handshake.py | Handshake local del MCP propio, sin Oracle | Active |
| add-type-hints.py | Type hints analysis utility | Active |
| audit_skill_ecosystem.py | Pre-commit ecosystem validation hook | Active |
| diagnose-apex-mcp-version.py | apex-mcp version diagnostics | Active |
| validate_apex_mcp_handshake.py | MCP initialize handshake validation | Diagnostic only (not used by bootstrap) |
| validate_apex_mcp_direct_connection.py | Direct Oracle connection validation | Active |
| Validate-ApexMcpApex241Compatibility.py | Retired internal-metadata validator | Disabled |
| Apply-ApexMcpApex241CompatibilityPatch.py | Retired internal-metadata patch | Disabled |
| Apply-ApexMcpDirectConnectionPatch.py | Preparación explícita y versionada fuera del bootstrap | Manual only |
