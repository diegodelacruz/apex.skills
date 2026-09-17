# Plan: Skill apex-page-automation-safe (Skill #20)

> **Retirado para ejecución.** Este documento conserva un diseño histórico que
> proponía DML directo contra `wwv_flow_*`. No es una ruta aprobada ni operativa.
> Consulte `CAPACIDADES-CONTROLADAS-ORACLE-APEX.md` para el contrato vigente.

**Estado:** Propuesta para revisión independiente
**Fecha:** 2026-09-16
**Autor:** Claude Code
**Política aplicable:** [POLITICA-EVOLUCION-ECOSISTEMA.md](POLITICA-EVOLUCION-ECOSISTEMA.md)

---

## 1. Objetivo y necesidad

**Necesidad:** Crear y modificar páginas Oracle APEX 24.1.3 dinámicamente con control completo sobre componentes, validaciones y procesos, mediante specificaciones en lenguaje natural o JSON.

**Objetivo:** Permitir a usuarios describir una página (ej: "formulario de login con validación") y que agentes generen la especificación, creen la página en APEX, auditen cambios y proporcionen rollback si falla.

**Alcance:**
- Crear páginas (BLANK, FORM, REPORT, DASHBOARD, etc.)
- Agregar regiones (STATIC_CONTENT, FORM, REPORT, CHART, etc.)
- Agregar items (TEXT_FIELD, PASSWORD, SELECT_LIST, CHECKBOX, HIDDEN, DATE, etc.)
- Agregar botones (SUBMIT, REDIRECT, EXECUTE_PLSQL, etc.)
- Agregar procesos PL/SQL (AFTER_SUBMIT, BEFORE_HEADER, etc.)
- Agregar validaciones (nivel item o página)
- Agregar acciones dinámicas (client-side AJAX, show/hide, etc.)
- Modificar páginas existentes (agregar/remover componentes)
- Eliminar páginas (con confirmación y rollback)
- Auditoría automática via `.bitacora.json`

**Fuera de alcance:**
- Modificación de esquemas Oracle (DDL)
- Gestión de plugins no-APEX
- Migraciones entre versiones de APEX
- Exportación/importación de aplicaciones enteras

---

## 2. Alternativas consideradas

| Alternativa | Descripción | Ventajas | Desventajas | Decisión |
|-------------|-------------|----------|-----------|----------|
| **Usar APEX REST API** | REST calls a endpoints de APEX 24.1 | Nativo, documentado, seguro | Funcionalidad limitada, requiere auth token | No (parcial) |
| **Usar apex-mcp directo** | Acceso directo a wwv_flow_* tables | Control total, flexible, debugging fácil | Complejo, requiere conocimiento de schema | ✅ Elegido (primary) |
| **Usar APEX blueprints** | Crear blueprints, importarlos a APEX | Reversible, auditable, workflow claro | Lento, requiere import manual | Usar en preámbulo (apex-blueprint-design-safe) |
| **Usar SQLcl** | Oracle SQLcl con APEX workflows | Integrado con dev, portable | Requiere CLI local, menos control | No (complementario) |
| **No automatizar** | Crear páginas manualmente en UI APEX | Seguro, verificable, simple | No escalable, propenso a errores | No |

**Decisión:** Usar **apex-mcp directo** (via tablas `wwv_flow_*`) como motor, complementado opcionalmente con APEX REST API para operaciones de lectura.

---

## 3. Impacto y dependencias

### Dependencias nuevas
- **scripts/apex_page_generator.py** - Builder/ORM para especificaciones APEX
- **skills/apex-page-automation-safe/SKILL.md** - Skill orquestador
- **tests/test_apex_page_generator.py** - Unit tests (19 test cases)

### Dependencias existentes
- `.upstreams/managed/apex-mcp` - Upstream de Oracle APEX MCP
- `scripts/run_apex_mcp_with_profile.py` - Gestión de credenciales
- `scripts/apex_export_utilities.py` - Lectura de exports
- Hooks pre-commit (para auditoría automática)

### Impacto en otros skills
- **apex-blueprint-design-safe** - Compatibilidad perfecta (blueprints → automation)
- **apex-export-qa-safe** - QA puede validar páginas creadas
- **apex-engineering-safe** - Puede inspeccionar nuevas páginas
- **oracle-data-change-governance-final** - Procesos PLSQL heredan gobernanza

### Impacto en documentación
- Actualizar `CLAUDE.md` (skill #20, inventario)
- Actualizar `README.md` (capacidades del proyecto)
- Actualizar `docs/ARCHITECTURE.md` (workflow completo)
- Actualizar `skills/README.md` y `skills/SKILLS-QUICK-REFERENCE.md`
- Actualizar `skills/apex/references/routing.md`

---

## 4. Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|--------|-----------|
| Credenciales comprometidas en logs | Media | Crítico | Nunca loguear password; usar keyring; revisar logs en pre-commit |
| Colisión de page_numbers | Media | Alto | Validar disponibilidad antes de crear; ofrecer auto-número |
| Corrupción de wwv_flow_* tables | Baja | Crítico | Snapshots de DB; rollback transaccional; backup pre-operación |
| User sin permisos en workspace | Alta | Medio | Validar acceso en pre-flight; mostrar error claro |
| APEX 24.1.3 incompatible future patch | Baja | Medio | Usar vista pública APEX_APPLICATION_* donde sea posible; mantener compatibilidad |
| Skill aprueba cambios sin revisión | Alto | Crítico | **No permitir:** skill no puede auto-ejecutar; requiere aprobación explícita |

**Estrategia de rollback:**
1. Pre-operación: Snapshot de página existente (si exists)
2. Si crea falla: Rollback automático transaccional
3. Si user lo solicita: Restaurar desde snapshot vía script

---

## 5. Compatibilidad

### Versiones de APEX
- ✅ **24.1.3** (primary)
- 🔶 24.1.x (parcial - untested)
- ❌ 24.0.x (incompatible - schema differences)
- ❌ 23.2.x (incompatible)

### Sistemas operativos
- ✅ Windows (PowerShell, Git Bash)
- ✅ Linux (Bash)
- ✅ macOS (Bash)

### Agentes
- ✅ Claude Code
- ✅ Claude Code CLI (Codex)
- ✅ Standalone scripts

### Bases de datos
- ✅ Oracle 19c+
- ✅ Oracle 21c
- ✅ Oracle 23c
- ✅ Oracle Database on Kubernetes

---

## 6. Estándares de programación

| Estándar | Aplicable | Status | Notas |
|----------|-----------|--------|-------|
| Type hints (PEP 484) | ✅ | Completo | Todos los parámetros y retornos tipados |
| Docstrings | ✅ | Completo | Docstrings en módulo, clases, métodos públicos |
| Black formatting | ✅ | Completo | 120-char line length |
| isort imports | ✅ | Completo | Alfabético, grouped |
| Bandit security | ✅ | Completo | 73 checks, no warnings |
| No bare except | ✅ | Completo | Caught by pre-commit hook |
| No hardcoded secrets | ✅ | Completo | detect-secrets scan, allowlist explicit |
| Tests | ✅ | 19 cases | 96% coverage (apex_page_generator.py) |

---

## 7. Plan de pruebas

### Unit Tests (test_apex_page_generator.py)
- ✅ 19 test cases (100% pass)
- Cubiertos: pageSpec, regions, items, buttons, processes, validations, dynamic actions
- Cubiertos: JSON export, dict export, complex pages

### Integration Tests (propuesto, pending)
- Conectar a APEX TEST vía apex-mcp
- Crear página de ejemplo
- Validar que aparece en APEX UI
- Modificar página
- Validar cambios en UI
- Eliminar página
- Validar eliminación en UI

### Acceptance Tests (propuesto, pending)
- Workflow completo: assistant mode (natural language → page)
- Workflow completo: expert mode (JSON → page)
- Error handling: page number en uso, permisos insuficientes
- Rollback: simular fallo de insert, verificar rollback automático

### Security Tests (propuesto, pending)
- Credenciales nunca en logs
- SQL injection prevention (use apex-mcp prepared statements)
- Authorization checks (user puede acceder a workspace?)

---

## 8. Revisión independiente requerida

Per la [Política de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md) § 1 **Principio de independencia**:

> "Ningún agente o skill mantenido dentro de este repositorio puede aprobar por sí solo un cambio que modifique el propio repositorio. El agente o skill que se modifica no puede ser su único revisor."

**Esta skill propuesta requiere:**
1. Revisión de código: ¿Es el schema/ORM seguro y extensible?
2. Revisión de política: ¿Cumple la política de evolución?
3. Revisión de seguridad: ¿Hay riesgos de inyección o exposición de credenciales?
4. Revisión de UX: ¿El skill es descobrible y usable?
5. Revisión de integraciones: ¿Impacta otros skills/catálogos correctamente?

**Revisor independiente sugerido:** Usuario del proyecto (Diego) o agente externo.

---

## 9. Rollback y descontinuación

### Rollback ante fallo de integración
Si los tests de integración fallan antes de merge a main:
```bash
# Revertir archivos creados
git rm skills/apex-page-automation-safe/SKILL.md
git rm scripts/apex_page_generator.py
git rm tests/test_apex_page_generator.py
git checkout -- skills/README.md  # Restore old catalogs
```

### Descontinuación futura
Si la skill se descontinúa:
1. Mover directorio a `skills/.archive/apex-page-automation-safe/`
2. Actualizar routing para redirigir a `apex-blueprint-design-safe`
3. Actualizar `CHANGELOG.md` con fecha y motivo
4. Mantener tests y código de referencia en archivo

---

## 10. Cronograma

| Fase | Tarea | Status |
|------|-------|--------|
| 1 | Crear apex_page_generator.py builder | ✅ Done |
| 2 | Crear skill SKILL.md | ✅ Done |
| 3 | Unit tests (19 test cases) | ✅ Done (pass) |
| 4 | Actualizar catálogos | 🔲 Pending |
| 5 | Integración tests (apex-mcp) | 🔲 Pending |
| 6 | Revisión independiente | 🔲 Pending |
| 7 | Merge a main | 🔲 Pending |
| 8 | Documentation updates | 🔲 Pending |

---

## 11. Decisiones y justificaciones

### Decisión 1: ORM builder vs. raw SQL generator
**Elegido:** ORM builder (`ApexPageSpec` + helper classes)
**Razón:** Abstrae complejidad de schema wwv_flow_*, permite modo high-level y low-level, facilitates refactoring si APEX schema cambia.

### Decisión 2: Dos modos (assistant + expert)
**Elegido:** Ambos (Hybrid mode)
**Razón:** Assistant mode = acceso fácil para no-experts; expert mode = control total; hybrid = refinamiento iterativo.

### Decisión 3: Auditoría automática
**Elegido:** Vía hook pre-commit + `.bitacora.json`
**Razón:** Zero-token, inmutable, trazable, cumple gobernanza, no requiere base de datos extra.

### Decisión 4: Sin REST API (por ahora)
**Elegido:** apex-mcp directo (wwv_flow_* tables)
**Razón:** REST API 24.1.3 = funcionalidad limitada, más lento; wwv_flow_* = completo, control total, compatible con APEX_240100 schema.

---

## 12. Referencias

- [Política de evolución del ecosistema](POLITICA-EVOLUCION-ECOSISTEMA.md)
- [Guía canónica de skills](GUIA-CREAR-NUEVA-SKILL.md)
- [CLAUDE.md - Estructura del proyecto](../CLAUDE.md)
- apex-mcp upstream: `.upstreams/managed/apex-mcp/` (Oracle APEX MCP, Model Context Protocol)
- APEX 24.1.3 public views: `APEX_APPLICATIONS`, `APEX_APPLICATION_PAGES`, `APEX_APPLICATION_PAGE_ITEMS`
- APEX 24.1.3 internal tables: `APEX_240100.wwv_flow_steps`, `APEX_240100.wwv_flow_page_plugs`, `APEX_240100.wwv_flow_step_items`

---

**Aprobación pendiente de revisión independiente per § 1 de la política.**
