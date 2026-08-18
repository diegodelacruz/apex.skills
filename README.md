# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3. Incluye base de patrones de exportes APEX, fuentes upstream, gobierno DATA, alineación TEST/Producción, QA y manuales Word.

## Preparación inicial

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

Use [la entrada canónica final](skills/CANONICAL-SKILLS-ULTIMATE.md): `apex-project-bootstrap-final`, seguido de `apex-delivery-lifecycle-complete`.

## Proyectos nuevos y diagnóstico

Cada proyecto contiene `control-proyecto/` para decisiones, plan maestro, cambios, scripts, QA, evidencia, releases y manuales. Consulte [estructura estándar](docs/estructura-estandar-proyecto.md) y [casos de uso](docs/casos-de-uso-apex.md).

El runtime Python compartido es `<RUTA_APEX_SKILLS>/.venv`. Cree `.venv` dentro de un proyecto sólo para dependencias propias, CI aislado o petición explícita.

## Credenciales y ambientes

Las credenciales TEST/Producción se guardan por usuario en el keyring seguro del sistema operativo, nunca en Git, `.env`, Markdown, SQL ni scripts. El inicializador importa el perfil desde el `.env` local sólo si aún no existe y verifica el MCP de TEST.

Antes de editar una página existente, aplique `apex-environment-alignment-complete`: compara TEST con Producción, registra el diff y recomienda sincronizar Producción a TEST si existen diferencias. La sincronización exige autorización explícita. Al concluir, el SQL validado de TEST y el manifiesto de instalación se guardan en `control-proyecto/cambios/<id>/release/`.

Lea [perfiles seguros](docs/perfiles-credenciales-seguros.md), [alineación de ambientes](docs/credenciales-y-alineacion-ambientes.md) y [configuración Codex Desktop](docs/codex-desktop-mcp-oracle.md).

## Políticas DATA

- Objetos oficiales: `data`; backups: esquema del usuario, sin depuración automática.
- Tablas: `id`, auditoría, `compania`, campos de negocio.
- Auditoría: `nvl(v('user'), 'ORCL')`.
- PK por defecto: `data.pk_commons.sp_secuencia('data.<table_name>', :new.id)`.
- Reconstrucción solo con solicitud explícita; no `alter` para correcciones de tablas/vistas.
- No crear claves, constraints ni índices sin petición explícita.

Las decisiones finales están en [decisiones canónicas](docs/decisiones-canonicas-finales.md).

## Upstreams y actualizaciones

El inicializador y actualizador V2 administran `apex-mcp`, `zaimella-skill` y `zaimella-apex-oracle`.

```powershell
.\scripts\Update-ApexSkillUpstreams-V2.ps1
.\scripts\Update-ApexSkillUpstreams-V2.ps1 -WhatIf
```

`apex-mcp` está orientado a 24.2; frente a APEX 24.1.3 se permite solo inspección/dry-run hasta una prueba de compatibilidad aprobada en TEST.

## Auditoría obligatoria

Después de cambios en skills, scripts o documentación:

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```

Consulte [auditoría obligatoria](docs/auditoria-obligatoria.md). El manual Word final requiere evidencia QA aprobada, auditoría de imágenes y renderizado a PNG para revisión visual antes de entregar.
