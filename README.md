# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3. Incluye conocimiento de Finanzas (109) y Compras (130), fuentes upstream, gobierno DATA, alineación TEST/Producción, QA y manuales Word.

## Preparación inicial

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
python -m pip install -r requirements.txt
python .\scripts\audit_skill_ecosystem.py
```

Use [la entrada canónica final](skills/CANONICAL-SKILLS-ULTIMATE.md): `apex-project-bootstrap-final`, seguido de `apex-delivery-lifecycle-complete`.

## Proyectos nuevos

Cada proyecto contiene `control-proyecto/` para decisiones, plan maestro, cambios, scripts, QA, evidencia, releases y manuales. Consulte [estructura estándar](docs/estructura-estandar-proyecto.md).

El runtime Python compartido es `<ruta-a-apex.skills>/.venv`. Cree `.venv` dentro de un proyecto solo para dependencias propias, CI aislado o petición explícita. Si falta una dependencia, el agente instala con aprobación automática o pregunta una vez antes de hacerlo.

## Credenciales y ambientes

Las credenciales TEST/Producción se guardan por usuario en el keyring seguro del sistema operativo, nunca en Git, `.env`, Markdown, SQL ni scripts.

```powershell
python .\scripts\manage_apex_credentials.py set --environment test
python .\scripts\manage_apex_credentials.py set --environment production
python .\scripts\manage_apex_credentials.py validate --environment test
```

Antes de editar una página existente, aplique `apex-environment-alignment-complete`: compara TEST con Producción, registra el diff y recomienda sincronizar Producción a TEST si existen diferencias. La sincronización exige autorización explícita. Al concluir, el SQL validado de TEST y el manifiesto de instalación se guardan en `control-proyecto/cambios/<id>/release/`.

Lea [perfiles seguros](docs/perfiles-credenciales-seguros.md) y [alineación de ambientes](docs/credenciales-y-alineacion-ambientes.md).

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

## Validación

Después de cambios en skills o documentación:

```powershell
python .\scripts\audit_skill_ecosystem.py
```

El manual Word final requiere evidencia QA aprobada, auditoría de imágenes y renderizado a PNG para revisión visual antes de entregar.
