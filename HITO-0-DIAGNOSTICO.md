# HITO 0: Diagnóstico Inicial
**Fecha:** 2026-09-17
**Responsable:** Claude Code
**Estado:** 🔄 EN PROGRESO

---

## 📊 Resumen Ejecutivo

| Métrica | Actual | Target | Brecha |
|---------|--------|--------|--------|
| **Test Coverage** | 43.34% | 92% | -48.66% |
| **Test Pass Rate** | 168/170 (98.8%) | 100% | 2 fallos |
| **Code Quality** | 75/100 | 90/100 | -15 pts |
| **Skills Conteo** | 21 SKILL.md | 19 SKILL.md | +2 (desalineado) |

---

## ✅ Test Results

**Total:** 170 tests
**Passed:** 168 ✅
**Failed:** 2 ❌

### Failed Tests:
1. **test_quality_audit_current_repository_passes**
   - Ubicación: `tests/test_quality_audit.py:20`
   - Error: `gates_pass` es False (esperado True)
   - Causa: Calidad del código no alcanza estándares

2. **test_skill_and_catalog_checks_use_current_inventory**
   - Ubicación: `tests/test_quality_audit.py:26`
   - Error: Encontró 21 SKILL.md, esperaba 19
   - Causa: Inventario desalineado (se agregaron 2 skills nuevas recientemente)

---

## 🔍 Coverage Analysis

### Coverage Global
- **Total:** 43.34%
- **Statements:** 1332 (706 sin coverage)
- **Branches:** 364 (39 sin cobertura)

### Scripts sin Coverage (0%)
Estos 11 archivos NO tienen NINGÚN test:
```
✗ Apply-ApexMcpApex241CompatibilityPatch.py       (33 statements)
✗ Apply-ApexMcpDirectConnectionPatch.py            (68 statements)
✗ Validate-ApexMcpApex241Compatibility.py         (26 statements)
✗ add-type-hints.py                               (142 statements)
✗ audit_skill_ecosystem.py                        (25 statements)
✗ diagnose-apex-mcp-version.py                    (44 statements)
✗ manage_apex_credentials.py                      (119 statements) ⚠️ CRÍTICO
✗ run_apex_mcp_with_profile.py                    (33 statements)
✗ validate-config.py                              (29 statements)
✗ validate_apex_mcp_direct_connection.py          (29 statements)
✗ validate_apex_mcp_handshake.py                  (26 statements)

TOTAL: 574 statements sin cobertura
```

### Scripts con Coverage Baja (<70%)
```
⚠️  path_setup.py                    38.10% (30 stmts, 16 sin coverage)
⚠️  apex_export_utilities.py         57.14% (35 stmts, 14 sin coverage)
⚠️  validate-oracle-documentation.py 62.01% (123 stmts, 43 sin coverage)
⚠️  audit_quality_score.py          77.92% (118 stmts, 23 sin coverage)
```

### Scripts con Coverage Bueno (>85%)
```
✅ apex_metadata.py                 94.44% (30 stmts)
✅ apex_page_generator.py           96.43% (140 stmts)
✅ cli_utils.py                     85.19% (27 stmts)
```

---

## 🔎 Deuda Técnica

### TODO/FIXME/XXX
Ejecutando búsqueda...

```
✓ No se encontraron TODOs activos en scripts/
✓ No se encontraron FIXMEs activos en scripts/
✓ No se encontraron XXXs activos en scripts/
```

### Problemas Detectados

1. **Inventario de Skills desalineado** (CRÍTICO)
   - Archivo: `tests/test_quality_audit.py:26`
   - Problema: 21 SKILL.md encontrados, pero tests esperan 19
   - Razón: Se agregaron 2 skills nuevas (commit a9a9b1c)
   - Solución: Actualizar test o catálogos

2. **manage_apex_credentials.py sin tests** (CRÍTICO)
   - 119 statements de lógica de manejo de credenciales
   - 0% coverage
   - Requiere 80+ tests unitarios

3. **Scripts de validación sin tests** (ALTO)
   - validate_apex_mcp_*.py (3 archivos)
   - add-type-hints.py
   - audit_skill_ecosystem.py
   - Estos son helpers pero requieren cobertura

4. **path_setup.py bajo coverage** (MEDIO)
   - 38.10% coverage
   - Necesita +5-10 tests para llegar a 85%+

5. **apex_export_utilities.py bajo coverage** (MEDIO)
   - 57.14% coverage
   - Necesita +3-5 tests para llegar a 85%+

---

## 📋 Checklist de Problemas a Resolver

### Problema 1: Inventario de Skills
- [ ] P1.1: Verificar cuántos SKILL.md hay actualmente
- [ ] P1.2: Actualizar test si hay 21 legítimamente
- [ ] P1.3: O actualizar catálogos si hay discrepancia

### Problema 2: Coverage Crítica
- [ ] P2.1: Crear tests para manage_apex_credentials.py (80+ tests)
- [ ] P2.2: Crear tests para validate_apex_mcp_*.py (40+ tests)
- [ ] P2.3: Crear tests para add-type-hints.py (20+ tests)
- [ ] P2.4: Crear tests para audit_skill_ecosystem.py (10+ tests)

### Problema 3: Coverage Baja
- [ ] P3.1: Aumentar path_setup.py a 85% (5-10 tests)
- [ ] P3.2: Aumentar apex_export_utilities.py a 85% (3-5 tests)
- [ ] P3.3: Aumentar validate-oracle-documentation.py a 85% (8-12 tests)
- [ ] P3.4: Aumentar audit_quality_score.py a 90% (3-5 tests)

### Problema 4: Code Quality
- [ ] P4.1: Ejecutar `black scripts/` para formateo
- [ ] P4.2: Ejecutar `isort scripts/` para imports
- [ ] P4.3: Agregar type hints completos (PEP 484)
- [ ] P4.4: Agregar docstrings faltantes
- [ ] P4.5: Resolver warnings de Bandit

---

## 📈 Plan de Acción

### Fase 1: Resolver Inventario (30 min)
1. Listar todos los SKILL.md en `skills/`
2. Actualizar test si hay 21 legítimamente
3. Validar que gates_pass = True

### Fase 2: Tests Críticos (5-6 horas)
1. Crear `tests/test_manage_apex_credentials.py` (80+ tests)
2. Crear `tests/test_validate_apex_mcp_*.py` (40+ tests)
3. Crear `tests/test_add_type_hints.py` (20+ tests)
4. Crear `tests/test_audit_skill_ecosystem.py` (10+ tests)

### Fase 3: Tests Coverage Baja (2-3 horas)
1. Aumentar path_setup.py: 38% → 85%
2. Aumentar apex_export_utilities.py: 57% → 85%
3. Aumentar validate-oracle-documentation.py: 62% → 85%
4. Aumentar audit_quality_score.py: 78% → 90%

### Fase 4: Refactoring de Código (2-3 horas)
1. Black formatting
2. isort
3. Type hints PEP 484
4. Docstrings
5. Bandit validation

### Estimación Total
- **Problemas encontrados:** 5 críticos/altos
- **Tests a crear:** 150+
- **Horas estimadas:** 10-12 horas
- **Meta final:** Coverage 92%, Quality 90/100

---

## 🎯 Criterio de Aceptación (HITO 0)

Para que HITO 0 pase auditoría:
- ✅ Test pass rate: 100% (170/170)
- ✅ Coverage: 92%+ en scripts/
- ✅ Code quality: 90+/100
- ✅ Bandit: 0 findings críticos
- ✅ Pre-commit: 0 errores
- ✅ No TODOs/FIXMEs activos

---

**Próximo paso:** Proceder con 0.2 (Aumentar Test Coverage)
