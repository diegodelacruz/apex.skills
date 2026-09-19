# Estrategia de Auditoría Independiente

**Estado:** obligatoria
**Versión:** 1.0
**Fecha:** 2026-09-19
**Ámbito:** todo cambio en `apex.skills`, sin importar el agente, el tipo de
archivo o el tamaño del cambio.

Este documento define la estrategia de auditoría en cinco niveles (L0-L4) para
el repositorio `apex.skills`. Complementa la
[Política canónica de evolución](../../docs/POLITICA-EVOLUCION-ECOSISTEMA.md)
y la [Matriz de cierre](../../docs/ACTUALIZACION-ECOSISTEMA.md) sin
reemplazarlas.

## Alcance estricto

Esta auditoría aplica **exclusivamente** al repositorio `apex.skills` y las
habilidades (skills) que contiene. Queda explícitamente fuera de alcance:

- **Proyectos del usuario:** ningún proyecto APEX, base de datos, aplicación
  o artefacto en el que el usuario esté trabajando.
- **Agentes y skills del repositorio:** los scripts de auditoría (L1, L2, L3)
  son independientes y desacoplados. No importan ni invocan skills,
  orquestadores ni scripts internos del framework (`scripts/cli_utils.py`,
  `scripts/apex_metadata.py`, etc.). Solo usan stdlib + yaml.
- **Juez y parte:** el repositorio no se audita a sí mismo con sus propias
  herramientas internas. Los auditores son scripts aislados que examinan
  el repositorio desde fuera de su cadena de dependencias.
- **Solo diagnosticar, nunca corregir:** la auditoría reporta hallazgos.
  No modifica, corrige ni elimina archivos como resultado de la ejecución.
  El usuario decide qué se corrige, cuándo y cómo.

## Principio rector

**El producto no puede auditarse a sí mismo.** Los validadores automatizados
(L0) son herramientas internas legítimas, pero no constituyen una auditoría
independiente. A partir de L1, el auditor no puede ser el autor del cambio, y
la auditoría debe ejecutarse sobre una revisión inmutable (commit específico).

## Niveles de auditoría

### L0 — Validación automatizada (CI)

**Cuándo:** cada commit y cada pull request.
**Quién ejecuta:** GitHub Actions (sin intervención humana).
**Independencia:** no requerida (es autovalidación determinística).

**Controles:**

| ID | Herramienta | Qué valida |
|---|---|---|
| L0-01 | `audit_skill_ecosystem.py` | Recursos requeridos + enlaces Markdown |
| L0-02 | `audit_quality_score.py` | 100 puntos, 9 dimensiones, gates bloqueantes |
| L0-03 | `post_impl_audit.py` | 10 checks post-implementación (P01-P10) |
| L0-04 | `pytest` | Suite de tests con cobertura |
| L0-05 | `black` + `isort` + `flake8` | Formato, imports, linting |
| L0-06 | `mypy` | Tipos estáticos |
| L0-07 | `bandit` | 52 checks de seguridad |
| L0-08 | `detect-secrets` | Exposición de credenciales |
| L0-09 | `git diff --check` | Errores de espacios en blanco |

**Gate:** L0 green es prerequisito para merge a `main`.

### L1 — Auditoría estructural independiente

**Cuándo:** después de cada cambio funcional, antes de declarar "listo".
**Quién ejecuta:** un agente o persona que NO sea el autor del cambio.
**Independencia:** obligatoria. El auditor se identifica en el reporte.

**Controles:**

| ID | Qué valida |
|---|---|
| L1-01 | Todos los directorios de skill tienen SKILL.md con frontmatter válido |
| L1-02 | `name` coincide con directorio, sin duplicados |
| L1-03 | Metadatos (category, order, tags) válidos y coherentes |
| L1-04 | Inventario real = routing = catálogos = README = CLAUDE.md |
| L1-05 | Enlaces Markdown resuelven a destinos existentes |
| L1-06 | Scripts, assets, plantillas referenciados existen |
| L1-07 | Configuración consistente (thresholds, conteos, versiones) |
| L1-08 | Imports coherentes (sin mezcla bare/qualified) |
| L1-09 | Archivos requeridos del ecosistema presentes |
| L1-10 | Estado Git limpio (sin archivos sin commit) |

**Herramienta:** `python scripts/post_impl_audit.py --report`
**Gate:** L1 PASS requerido para release menor.

### L2 — Auditoría de seguridad independiente

**Cuándo:** trimestralmente, y ante cambios que toquen credenciales, MCP,
Oracle, PowerShell o CI.
**Quién ejecuta:** un auditor de seguridad independiente (persona o agente
especializado que NO haya participado en el desarrollo).
**Independencia:** obligatoria. El auditor no debe tener commits en la rama
auditada.

**Controles:**

| ID | Qué valida |
|---|---|
| L2-01 | No hay secrets en archivos Python, PowerShell, YAML, JSON |
| L2-02 | No hay credenciales Oracle hardcodeadas (patrones TNS, passwords) |
| L2-03 | Perfiles MCP no contienen datos sensibles en texto plano |
| L2-04 | Variables de entorno con secrets están sanitizadas |
| L2-05 | No hay SQL injection patterns en scripts |
| L2-06 | Baseline de detect-secrets está actualizada |
| L2-07 | Dependencias no tienen vulnerabilidades conocidas (CVE) |
| L2-08 | Threat model (SECURITY-THREATS.md) está vigente |
| L2-09 | Pre-commit hooks de seguridad están activos y no bypaseados |
| L2-10 | Archivos .env.example no contienen valores reales |

**Herramienta:** `python scripts/audit_security_checklist.py --report`
**Gate:** L2 PASS requerido para release mayor.

### L3 — Auditoría semántica

**Cuándo:** antes de cada release mayor, y cuando se agreguen o modifiquen
skills.
**Quién ejecuta:** un agente o persona que valide que la documentación
coincide con el comportamiento real.
**Independencia:** obligatoria.

**Controles:**

| ID | Qué valida |
|---|---|
| L3-01 | Cada SKILL.md tiene al menos un ejemplo de uso |
| L3-02 | Tags de cada skill corresponden a capacidades reales |
| L3-03 | Routing en `apex/references/routing.md` mapea a skills existentes |
| L3-04 | Categorías en CLAUDE.md coinciden con YAML frontmatter |
| L3-05 | references/ declaradas en SKILL.md existen y son legibles |
| L3-06 | Scripts referenciados en skills son sintácticamente válidos |
| L3-07 | Descripciones de skills son precisas (no prometen más de lo que hacen) |
| L3-08 | Archivos en scripts/ y docs/ huérfanos (no referenciados por ningún otro archivo) |
| L3-09 | Documentación clave con fecha "Last Updated" vigente (máximo 180 días) |
| L3-10 | Conteos de skills en CLAUDE.md y skills/README.md coinciden con la realidad |

**Herramienta:** `python scripts/audit_semantic_checks.py --report`
**Gate:** L3 PASS requerido antes de primera adopción por equipo externo.

### L4 — Auditoría piloto (uso real)

**Cuándo:** antes de producción APEX, y antes de onboarding de equipos
externos.
**Quién ejecuta:** un tester externo que no conozca la implementación interna.
**Independencia:** obligatoria. El tester no debe ser contribuidor del
repositorio.

**Controles:**

| ID | Qué valida |
|---|---|
| L4-01 | Bootstrap de proyecto APEX completa sin errores |
| L4-02 | Invocación de `/apex` rutea correctamente al menos 3 skills |
| L4-03 | Skill de ingeniería produce artefacto válido en entorno TEST |
| L4-04 | Skill de QA detecta un defecto plantado intencionalmente |
| L4-05 | Documentación permite completar una tarea sin asistencia del autor |
| L4-06 | Tiempo para completar tarea está dentro del rango esperado |

**Herramienta:** manual, con plantilla `governance/audit/plantillas/reporte-L4.md`
**Gate:** L4 PASS requerido para producción APEX y onboarding externo.

## Release gates

| Gate | Niveles requeridos | Cuándo aplica |
|---|---|---|
| Merge a main (PR) | L0 green | Todo cambio |
| Release menor (skill nueva, fix) | L0 + L1 PASS | Cambios funcionales |
| Release mayor (nueva versión) | L0 + L1 + L2 PASS | Cambios estructurales |
| Primera adopción por equipo externo | L0 + L1 + L2 + L3 PASS | Nuevos consumidores |
| Producción APEX (cambios Oracle) | L0 + L1 + L2 + L4 PASS | Cualquier DML/DDL |

## Independencia y rotación

### Regla de independencia

- **L0:** no aplica (automatizado).
- **L1-L4:** el auditor NO puede ser el autor del cambio auditado.
- El reporte debe registrar la identidad del auditor y declarar explícitamente
  que no participó en el desarrollo.

### Rotación

- Para auditorías L2+, no se debe usar el mismo auditor más de 3 veces
  consecutivas sobre el mismo scope.
- El registro central (`REGISTRO-AUDITORIAS.md`) permite verificar esta regla.

## Registro central

Toda auditoría L1+ debe registrarse en
[`governance/audit/REGISTRO-AUDITORIAS.md`](REGISTRO-AUDITORIAS.md) con:
audit_id, nivel, fecha, revisión, auditor, resultado, y ruta al reporte.

## Hallazgos

Cada hallazgo sigue el ciclo de vida:

```
ABIERTO → ASIGNADO → RESUELTO → VERIFICADO
```

Severidades:

| Severidad | Definición | Acción |
|---|---|---|
| CRITICO | Bloquea operación o expone datos sensibles | Fix inmediato, bloquea release |
| ALTO | Funcionalidad incorrecta o riesgo de seguridad | Fix antes de release |
| MEDIO | Inconsistencia documentada, degradación menor | Fix planificado |
| BAJO | Mejora recomendada, no afecta operación | Backlog |
| INFO | Observación, sin acción requerida | Registro |

Hallazgos CRITICO y ALTO son bloqueantes. Su resolución requiere verificación
por el auditor original o un auditor independiente.

## Relación con documentos existentes

| Documento existente | Relación |
|---|---|
| `POLITICA-EVOLUCION-ECOSISTEMA.md` | Política matriz. Esta estrategia la operacionaliza. |
| `ACTUALIZACION-ECOSISTEMA.md` | Matriz C01-C15 se mapea a controles L1. |
| `auditoria-obligatoria.md` | Comandos mínimos se incorporan en L0. |
| `MATRIZ-CALIDAD-INTERAGENTES.md` | Score de 100 puntos es control L0-02. |
| `SECURITY-THREATS.md` | Threat model alimenta controles L2. |
| `AGENTS.md` | Regla de independencia reforzada aquí. |
