# Reporte de Auditoría L3 — Semántica

| Campo | Valor |
|---|---|
| **audit_id** | AUD-AAAA-MMDD-L3-NNN |
| **nivel** | L3 |
| **fecha** | AAAA-MM-DDTHH:MM:SS-05:00 |
| **revision** | (commit SHA completo) |
| **scope** | full-repository |
| **auditor** | (identidad del auditor) |
| **es_autor_del_cambio** | false |
| **resultado** | PASS / FAIL / PASS_WITH_OBSERVATIONS |

## Declaración de independencia

Declaro que no participé en el desarrollo de los cambios auditados y que
valido la correspondencia entre documentación y comportamiento real desde una
perspectiva externa.

## Resumen ejecutivo

(1-3 oraciones: qué se validó semánticamente, consistencia encontrada,
gaps entre documentación y realidad)

## Controles ejecutados

| ID | Control | Resultado | Hallazgos |
|---|---|---|---|
| L3-01 | SKILL.md con ejemplo de uso | PASS/FAIL | |
| L3-02 | Tags corresponden a capacidades reales | PASS/FAIL | |
| L3-03 | Routing mapea a skills existentes | PASS/FAIL | |
| L3-04 | Categorías CLAUDE.md = YAML frontmatter | PASS/FAIL | |
| L3-05 | references/ declaradas existen | PASS/FAIL | |
| L3-06 | Scripts referenciados son válidos | PASS/FAIL | |
| L3-07 | Descripciones son precisas | PASS/FAIL | |

## Hallazgos

| ID | Severidad | Control | Descripción | Archivo | Estado |
|---|---|---|---|---|---|
| H-NNN | CRITICO/ALTO/MEDIO/BAJO/INFO | L3-XX | | | ABIERTO |

## Observaciones semánticas

(Skills que prometen más de lo que hacen. Documentación ambigua. Ejemplos
desactualizados. Tags que no reflejan la capacidad real.)

## Conclusión

(Resultado final. Recomendaciones para alinear documentación con realidad.)

## Evidencia

- Comando ejecutado: `python scripts/audit_semantic_checks.py --report`
- Revisión manual de skills: (lista)
- Hora de ejecución: (timestamp)
