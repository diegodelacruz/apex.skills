# Reporte de Auditoría L1 — Estructura e Integridad

| Campo | Valor |
|---|---|
| **audit_id** | AUD-AAAA-MMDD-L1-NNN |
| **nivel** | L1 |
| **fecha** | AAAA-MM-DDTHH:MM:SS-05:00 |
| **revision** | (commit SHA completo) |
| **scope** | full-repository |
| **auditor** | (identidad del auditor) |
| **es_autor_del_cambio** | false |
| **resultado** | PASS / FAIL / PASS_WITH_OBSERVATIONS |

## Declaración de independencia

Declaro que no participé en el desarrollo de los cambios auditados en la
revisión indicada. No tengo commits en la rama auditada posteriores al punto
base desde el cual se ejecutó esta auditoría.

## Resumen ejecutivo

(1-3 oraciones: qué se auditó, resultado general, observaciones clave)

## Controles ejecutados

| ID | Control | Resultado | Hallazgos |
|---|---|---|---|
| L1-01 | SKILL.md con frontmatter válido | PASS/FAIL | |
| L1-02 | name = directorio, sin duplicados | PASS/FAIL | |
| L1-03 | Metadatos válidos y coherentes | PASS/FAIL | |
| L1-04 | Inventario = routing = catálogos | PASS/FAIL | |
| L1-05 | Enlaces Markdown resuelven | PASS/FAIL | |
| L1-06 | Scripts/assets referenciados existen | PASS/FAIL | |
| L1-07 | Configuración consistente | PASS/FAIL | |
| L1-08 | Imports coherentes | PASS/FAIL | |
| L1-09 | Archivos requeridos presentes | PASS/FAIL | |
| L1-10 | Estado Git limpio | PASS/FAIL | |

## Hallazgos

| ID | Severidad | Control | Descripción | Archivo | Estado |
|---|---|---|---|---|---|
| H-NNN | CRITICO/ALTO/MEDIO/BAJO/INFO | L1-XX | | | ABIERTO |

## Conclusión

(Resultado final. Si FAIL: qué debe corregirse antes de cerrar. Si
PASS_WITH_OBSERVATIONS: qué se recomienda sin ser bloqueante.)

## Evidencia

- Comando ejecutado: `python scripts/post_impl_audit.py --report`
- Salida completa: (adjuntar o referenciar)
- Hora de ejecución: (timestamp)
