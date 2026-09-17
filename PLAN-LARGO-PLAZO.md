# PLAN DE LARGO PLAZO: apex.skills Transformation
**Versión:** 1.0
**Fecha Inicio:** 2026-09-17
**Duración Estimada:** 16-18 semanas
**Estado:** 🔵 EN PLANIFICACIÓN

---

## 🎯 Objetivo Final

Transformar `apex.skills` en una **plataforma de generación automática de aplicaciones APEX**, donde:
- **INPUT:** Requisitos en Markdown simple
- **OUTPUT:** Aplicación APEX funcional (80% scaffolding automático) en 1-2 horas
- **CALIDAD:** Auditable, testeado, documentado

---

## 📊 Timeline Visual

```
Sem 1-3:  FASE 0 [████████]
Sem 4-7:  FASE 1 [████████]  |  FASE 2 [████████]
Sem 4-9:  FASE 3 [████████████████]  |  FASE 4 [████████████████]
Sem 10-12: FASE 5 [████████]
```

---

## 🏆 HITO 0: Fundación Sólida (Semanas 1-3)

### Objetivo
Aumentar test coverage de 80% → 92% y code quality de 75% → 90%.
Base confiable para nuevas skills.

### 📋 Checklist de Actividades

#### 0.1 Diagnóstico Inicial ✅
- [x] **0.1.1** Ejecutar `pytest tests/ --cov=scripts --cov-report=html`
- [x] **0.1.2** Documentar gaps de coverage (qué archivos/funciones faltan tests)
- [x] **0.1.3** Ejecutar `grep -r "TODO\|FIXME\|XXX" scripts/` para deuda técnica
- [x] **0.1.4** Revisar warnings de Flake8 en `scripts/`
- [x] **0.1.5** Generar reporte de code quality (black, isort, bandit)

**Criterio de Aceptación:**
- Documento `HITO-0-DIAGNOSTICO.md` con:
  - Coverage gaps identificados
  - TODO/FIXME/XXX listados
  - Archivos prioritarios para refactoring

---

#### 0.2 Aumentar Test Coverage (80% → 92%)
- [x] **0.2.1** Agregar tests para `path_setup.py` (coverage: 38% → 85.71%) ✅
- [x] **0.2.2** Agregar tests para `manage_apex_credentials.py` (coverage: 0% → 35.10%) ✅
- [ ] **0.2.3** Agregar tests para `validate_apex_mcp_*.py` (0% → 70%+)
- [ ] **0.2.4** Agregar tests para `run_apex_mcp_with_profile.py` (0% → 70%+)
- [ ] **0.2.5** Agregar tests para `audit_skill_ecosystem.py` (0% → 70%+)
- [ ] **0.2.6** Ejecutar `pytest tests/ --cov` y verificar 70%+ coverage global

**Criterio de Aceptación:**
- `pytest tests/ --cov=scripts` muestra **≥92% coverage**
- Todos los tests pasan: `pytest tests/ -v`
- Archivo `tests/mocks/` contiene fixtures para APEX/MCP/REST

---

#### 0.3 Refactoring de Code Quality (75% → 90%)
- [ ] **0.3.1** Aplicar Black formatting: `black scripts/`
- [ ] **0.3.2** Aplicar isort: `isort scripts/`
- [ ] **0.3.3** Agregar type hints completos (PEP 484) a `cli_utils.py`
- [ ] **0.3.4** Agregar type hints completos a `apex_metadata.py`
- [ ] **0.3.5** Agregar docstrings a funciones privadas (Google style)
- [ ] **0.3.6** Resolver todos los warnings de Bandit (seguridad)
- [ ] **0.3.7** Ejecutar pre-commit hooks: `pre-commit run --all-files`

**Criterio de Aceptación:**
- `flake8 scripts/` no muestra errores (solo warnings menores)
- `mypy scripts/` válida tipos correctamente
- `bandit -r scripts/` sin findings críticos
- Pre-commit hooks pasan 100%

---

#### 0.4 Eliminar Deuda Técnica
- [ ] **0.4.1** Remover TODO/FIXME que están resueltos
- [ ] **0.4.2** Refactorizar funciones complejas (>20 líneas)
- [ ] **0.4.3** Consolidar funciones duplicadas
- [ ] **0.4.4** Documentar funciones no obvias

**Criterio de Aceptación:**
- No hay TODO/FIXME activos en `scripts/`
- Funciones complejas refactorizadas (máx 20 líneas)
- Documentación clara en funciones no obvias

---

#### 0.5 Validación de Score
- [ ] **0.5.1** Ejecutar diagnóstico final de calidad
- [ ] **0.5.2** Documentar scores finales en `HITO-0-RESULTADO.md`
- [ ] **0.5.3** Comparar con baseline: 82/100 → 90+/100

**Criterio de Aceptación:**
- Overall Score: **90/100+**
- Code Quality: **90/100+**
- Testing: **92/100+**

---

### 🔍 Auditoría Desacoplada (HITO 0)

**Responsable:** Claude Code (revisión independiente)

**Procedimiento:**
1. Checkout rama `hito-0-foundation` (nueva rama)
2. Ejecutar suite de validación:
   ```bash
   pytest tests/ -v --cov=scripts --cov-report=term
   pre-commit run --all-files
   flake8 scripts/ --max-line-length=120
   mypy scripts/
   bandit -r scripts/ -v
   ```
3. Revisar `HITO-0-RESULTADO.md` con métricas finales
4. Si **pasa auditoría** → Merge a `main` con commit:
   ```
   feat(quality): HITO-0 - Fortalecer fundación (82 → 90 score)

   - Test coverage: 80% → 92%
   - Code quality: 75% → 90%
   - Deuda técnica eliminada
   - Pre-commit hooks validados
   ```

**Criterios de Paso:**
- ✅ pytest: 92%+ coverage, 100% pass rate
- ✅ pre-commit: 0 errores
- ✅ Code quality: 90+/100
- ✅ No TODOs/FIXMEs activos
- ✅ Documentación: `HITO-0-RESULTADO.md` completo

**Si falla:** Volver a checklist, ajustar, re-auditar.

---

## 🏆 HITO 1: Code Generation Safe (Semanas 4-7)

### Objetivo
Generar código APEX automáticamente: Forms, Reports, validaciones, JavaScript.

### 📋 Checklist de Actividades

#### 1.1 Estructura de Skill
- [ ] **1.1.1** Crear directorio `/skills/apex-code-generation-safe/`
- [ ] **1.1.2** Crear estructura base: `README.md`, `SKILL.md`, `__init__.py`
- [ ] **1.1.3** Crear `scripts/apex_code_generators.py` con clases base
- [ ] **1.1.4** Crear `tests/test_apex_code_generators.py`

**Criterio de Aceptación:**
- Estructura de skill lista
- Tests pueden importar módulos sin errores
- Documentación de API inicial en `SKILL.md`

---

#### 1.2 ApexFormGenerator
- [ ] **1.2.1** Implementar `ApexFormGenerator` class
- [ ] **1.2.2** Método: `generate_from_table(table_name)` → APEX Form JSON
- [ ] **1.2.3** Método: `add_validation_rules()`
- [ ] **1.2.4** Método: `add_readonly_fields()`
- [ ] **1.2.5** Generar validaciones PL/SQL automáticas
- [ ] **1.2.6** Unit tests: 90%+ coverage

**Criterio de Aceptación:**
- `generate_from_table('EMPLOYEES')` produce Form APEX válido
- Validaciones generadas automáticamente
- Tests: 10+ casos de prueba, 90%+ coverage

---

#### 1.3 ApexReportGenerator
- [ ] **1.3.1** Implementar `ApexReportGenerator` class
- [ ] **1.3.2** Método: `generate_from_query(sql_query)` → APEX Report JSON
- [ ] **1.3.3** Método: `add_columns_formatting()`
- [ ] **1.3.4** Método: `add_filters()`
- [ ] **1.3.5** Generar JavaScript para interactividad
- [ ] **1.3.6** Unit tests: 90%+ coverage

**Criterio de Aceptación:**
- `generate_from_query('SELECT ...')` produce Report APEX válido
- Formatos (moneda, fecha) aplicados automáticamente
- Tests: 10+ casos, 90%+ coverage

---

#### 1.4 ApexValidationGenerator
- [ ] **1.4.1** Implementar `ApexValidationGenerator` class
- [ ] **1.4.2** Generar validaciones PL/SQL: required, unique, range
- [ ] **1.4.3** Generar validaciones JavaScript: client-side
- [ ] **1.4.4** Manejar custom validations (regex, business rules)
- [ ] **1.4.5** Unit tests: 90%+ coverage

**Criterio de Aceptación:**
- PL/SQL válido y ejecutable en Oracle
- JavaScript funciona en navegador
- Tests: 15+ casos, 90%+ coverage

---

#### 1.5 ApexJavaScriptGenerator
- [ ] **1.5.1** Implementar `ApexJavaScriptGenerator` class
- [ ] **1.5.2** Generar: item interactions, conditional display, calculations
- [ ] **1.5.3** Generar: validaciones client-side
- [ ] **1.5.4** Generar: llamadas a AJAX/REST
- [ ] **1.5.5** Unit tests: 90%+ coverage

**Criterio de Aceptación:**
- JavaScript válido y funcional
- Integra con APEX dinamicamente
- Tests: 12+ casos, 90%+ coverage

---

#### 1.6 Integración y Tests End-to-End
- [ ] **1.6.1** Integrar con `apex-schema-automation-safe`
- [ ] **1.6.2** Test: generar form desde tabla existente
- [ ] **1.6.3** Test: generar report desde query existente
- [ ] **1.6.4** Test: validar output en APEX Workspace (manual)
- [ ] **1.6.5** Documentación de flujos en `SKILL.md`

**Criterio de Aceptación:**
- Generadores integrados funcionan juntos
- Output validado en APEX (manual)
- Documentación con 5+ ejemplos prácticos

---

#### 1.7 Documentación y Ejemplos
- [ ] **1.7.1** Escribir `SKILL.md` con metadata y descripción
- [ ] **1.7.2** Crear 5 ejemplos ejecutables en `skills/apex-code-generation-safe/examples/`
- [ ] **1.7.3** Escribir guía de contribución
- [ ] **1.7.4** Documentar API en docstrings

**Criterio de Aceptación:**
- `SKILL.md` completo y claro
- 5+ ejemplos funcionales
- API documentada en 100% de funciones públicas

---

### 🔍 Auditoría Desacoplada (HITO 1)

**Responsable:** Claude Code (revisión independiente)

**Procedimiento:**
1. Checkout rama `hito-1-codegen` (nueva rama)
2. Ejecutar validación:
   ```bash
   pytest tests/test_apex_code_generators.py -v --cov
   pre-commit run --all-files
   # Validar output manual en APEX Workspace
   ```
3. Revisar `HITO-1-RESULTADO.md`
4. Si **pasa auditoría** → Merge a `main`

**Criterios de Paso:**
- ✅ Tests: 90%+ coverage, 100% pass rate
- ✅ Output APEX válido (verificado manual)
- ✅ `SKILL.md` documentado
- ✅ Ejemplos funcionales

---

## 🏆 HITO 2: API Client Safe (Semanas 4-7) - PARALELO A HITO 1

### Objetivo
Cliente REST para APEX: crear apps, deploy, sincronizar ambientes.

### 📋 Checklist de Actividades

#### 2.1 Estructura de Skill
- [ ] **2.1.1** Crear directorio `/skills/apex-api-client-safe/`
- [ ] **2.1.2** Crear `scripts/apex_rest_client.py`
- [ ] **2.1.3** Crear `tests/test_apex_rest_client.py`

---

#### 2.2 ApexRestClient Base
- [ ] **2.2.1** Implementar clase `ApexRestClient`
- [ ] **2.2.2** Autenticación: OAuth2 + token caching
- [ ] **2.2.3** Manejo de errores y reintentos (exponential backoff)
- [ ] **2.2.4** Logging de todas las llamadas REST
- [ ] **2.2.5** Unit tests: 90%+ coverage

---

#### 2.3 Métodos CRUD de Aplicaciones
- [ ] **2.3.1** `create_application(config_dict)` → app_id
- [ ] **2.3.2** `get_application(app_id)` → metadata
- [ ] **2.3.3** `update_application(app_id, config)`
- [ ] **2.3.4** `delete_application(app_id)`
- [ ] **2.3.5** Unit tests: 15+ casos

---

#### 2.4 Métodos de Deployment
- [ ] **2.4.1** `export_application(app_id)` → ZIP bytes
- [ ] **2.4.2** `import_application(zip_file)` → app_id
- [ ] **2.4.3** `deploy_to_environment(app_id, target_env)`
- [ ] **2.4.4** Validación pre-deploy (checks)
- [ ] **2.4.5** Rollback en caso de error
- [ ] **2.4.6** Unit tests: 20+ casos

---

#### 2.5 Sincronización de Ambientes
- [ ] **2.5.1** `sync_between_environments(app_id, source_env, target_env)`
- [ ] **2.5.2** Detectar diferencias automáticamente
- [ ] **2.5.3** Merge de cambios inteligente
- [ ] **2.5.4** Audit trail de sincronización
- [ ] **2.5.5** Unit tests: 15+ casos

---

#### 2.6 Integración y Documentación
- [ ] **2.6.1** Integrar con `apex-delivery-lifecycle-safe`
- [ ] **2.6.2** Tests end-to-end (mocked APEX)
- [ ] **2.6.3** `SKILL.md` con flujos completos
- [ ] **2.6.4** 5+ ejemplos de uso

---

### 🔍 Auditoría Desacoplada (HITO 2)

**Criterios de Paso:**
- ✅ Tests: 90%+ coverage, 100% pass rate
- ✅ REST calls mockeados correctamente
- ✅ Error handling robusto
- ✅ Documentación completa

---

## 🏆 HITO 3: Automated Testing Safe (Semanas 4-9)

### Objetivo
Testing automatizado: Selenium, validación de UI, performance.

### 📋 Checklist de Actividades

#### 3.1 ApexTestGenerator
- [ ] **3.1.1** Crear `scripts/apex_test_generator.py`
- [ ] **3.1.2** Generar Selenium tests desde APEX page metadata
- [ ] **3.1.3** Generar tests de login
- [ ] **3.1.4** Generar tests de CRUD
- [ ] **3.1.5** Generar tests de validaciones

---

#### 3.2 ApexPerformanceTester
- [ ] **3.2.1** Medir page load time
- [ ] **3.2.2** Detectar n+1 queries
- [ ] **3.2.3** Validar responsiveness

---

#### 3.3 ApexRegressionValidator
- [ ] **3.3.1** Comparar con baseline
- [ ] **3.3.2** Detectar cambios no esperados

---

#### 3.4 CI/CD Integration
- [ ] **3.4.1** Integrar con delivery-lifecycle
- [ ] **3.4.2** Generar reportes de test

---

### 🔍 Auditoría Desacoplada (HITO 3)

**Criterios de Paso:**
- ✅ Tests: 90%+ coverage
- ✅ Selenium tests funcionales (con mock)
- ✅ Performance testing implementado

---

## 🏆 HITO 4: Data Migration Safe (Semanas 4-9)

### Objetivo
Migración segura de datos legacy: mapeo, validación, rollback.

### 📋 Checklist de Actividades

#### 4.1 SchemaMapper
- [ ] **4.1.1** Crear `scripts/apex_data_migration.py`
- [ ] **4.1.2** Auto-mapeo: legacy schema → APEX schema
- [ ] **4.1.3** Validación de tipos de datos

---

#### 4.2 DataValidator
- [ ] **4.2.1** Pre-migration checks
- [ ] **4.2.2** Post-migration validation

---

#### 4.3 DataTransformer
- [ ] **4.3.1** ETL: extract, transform, load
- [ ] **4.3.2** Manejo de datos sensibles

---

#### 4.4 RollbackManager
- [ ] **4.4.1** Crear savepoints
- [ ] **4.4.2** Rollback automático

---

### 🔍 Auditoría Desacoplada (HITO 4)

**Criterios de Paso:**
- ✅ Tests: 90%+ coverage
- ✅ Data integrity validada
- ✅ Rollback funciona correctamente

---

## 🏆 HITO 5: Application Generator Complete (Semanas 10-12)

### Objetivo
Orquestador maestro que encadena todas las skills.

### 📋 Checklist de Actividades

#### 5.1 ApplicationBuilder Orchestrator
- [ ] **5.1.1** Crear `scripts/apex_application_builder.py`
- [ ] **5.1.2** Clase `ApplicationBuilder` que orquesta todas las skills
- [ ] **5.1.3** Flujo: requisitos → app funcional

---

#### 5.2 Requisitos YAML Schema
- [ ] **5.2.1** Definir schema YAML para requisitos
- [ ] **5.2.2** Validar input contra schema
- [ ] **5.2.3** Generar template de requisitos

---

#### 5.3 Integración Completa
- [ ] **5.3.1** Encadenar: code-gen → api-client → testing → migration
- [ ] **5.3.2** Manejo de errores en cada paso
- [ ] **5.3.3** Reporte de progreso

---

#### 5.4 End-to-End Test
- [ ] **5.4.1** Generar app completa desde requisitos
- [ ] **5.4.2** Validar en APEX Workspace
- [ ] **5.4.3** Medir tiempo de generación

---

### 🔍 Auditoría Desacoplada (HITO 5)

**Criterios de Paso:**
- ✅ App generada end-to-end
- ✅ Tiempo: 1-2 horas (vs 5-6 manual)
- ✅ 80%+ scaffolding automático
- ✅ Documentación completa

---

## 📈 Métricas de Éxito Global

| Métrica | Baseline | Target | Status |
|---------|----------|--------|--------|
| Overall Score | 82/100 | 95/100 | ⏳ |
| Code Quality | 75/100 | 92/100 | ⏳ |
| Testing | 80/100 | 94/100 | ⏳ |
| Test Coverage | 80% | 92% | ⏳ |
| Skills Nuevas | 0 | 4 | ⏳ |
| Tiempo Generación App | 5-6h | 1-2h | ⏳ |
| Automatización | 40% | 95% | ⏳ |

---

## 🔄 Proceso de Cada Hito

### Antes de Auditoría
1. ✅ Completar todas las actividades del checklist
2. ✅ Todos los tests pasan (pytest)
3. ✅ Pre-commit hooks validan
4. ✅ Documentación está completa
5. ✅ Crear rama `hito-N` con cambios

### Durante Auditoría
1. 🔍 Revisión independiente de cambios
2. 🔍 Validar criterios de aceptación
3. 🔍 Ejecutar suite de validación
4. 🔍 Si pasa → Merge a `main` + tag `hito-N-complete`

### Después de Auditoría (Si Pasa)
```bash
git tag -a hito-N-complete -m "HITO N: descripción"
git push origin hito-N-complete
# Commit automático con audit trail
```

---

## 📝 Plantillas de Documentación

### HITO-N-DIAGNOSTICO.md
```markdown
# Diagnóstico HITO N

**Fecha:** 2026-XX-XX
**Estado:** Inicio

## Findings
- [x] Issue 1
- [x] Issue 2

## Plan
1. Actividad 1
2. Actividad 2
```

### HITO-N-RESULTADO.md
```markdown
# Resultado HITO N

**Fecha:** 2026-XX-XX
**Estado:** ✅ COMPLETO

## Métricas Finales
- Coverage: 92%
- Score: 90/100
- Tests: 100% pass

## Cambios
- [x] Feature 1
- [x] Feature 2

## Auditoría
- ✅ Pase pre-commit
- ✅ 90%+ coverage
- ✅ Documentación completa
```

---

## 🚀 Estado Actual

| Hito | Estado | Progreso | Inicio | Fin |
|------|--------|----------|--------|-----|
| **HITO 0** | 🔴 PENDIENTE | 0% | - | - |
| **HITO 1** | 🔴 PENDIENTE | 0% | - | - |
| **HITO 2** | 🔴 PENDIENTE | 0% | - | - |
| **HITO 3** | 🔴 PENDIENTE | 0% | - | - |
| **HITO 4** | 🔴 PENDIENTE | 0% | - | - |
| **HITO 5** | 🔴 PENDIENTE | 0% | - | - |

---

## 📞 Próximos Pasos

1. ✅ **Revisar este plan** (conversación)
2. ✅ **Ajustar si es necesario**
3. 🚀 **Aprobar inicio HITO 0**
4. 🚀 **Comenzar desarrollo**

---

**Última actualización:** 2026-09-17
**Responsable:** Claude Code + Diego de La Cruz
