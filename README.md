# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3 y objetos Oracle relacionados.

La calidad del repositorio se mide con la [Matriz de calidad interagentes](docs/MATRIZ-CALIDAD-INTERAGENTES.md) y el auditor reproducible `python .\scripts\audit_quality_score.py`; un `FAIL` bloquea la publicación.

**Inventario actual:** 21 skills portables, verificadas por el auditor.

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

Para validar TEST/MCP, ejecute después Initialize-ApexCodexProject.ps1 con el proyecto y las aprobaciones correspondientes.

## Principios

- Perfiles TEST/Producción seguros por usuario; sin secretos en Git o documentación.
- Validación de acceso en lectura antes de operar un ambiente.
- Alineación TEST/Producción para páginas existentes y control de rangos por proyecto.
- Cambios a Producción sólo con aprobación explícita separada.
- Gobierno DATA, decisiones, planes, validación SQL y auditoría antes del cierre.

Consulte [dependencias](docs/dependencias.md), [casos de uso](docs/casos-de-uso-apex.md) y [auditoría obligatoria](docs/auditoria-obligatoria.md).
