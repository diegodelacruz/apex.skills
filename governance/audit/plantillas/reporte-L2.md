# Reporte de Auditoría L2 — Seguridad

| Campo | Valor |
|---|---|
| **audit_id** | AUD-AAAA-MMDD-L2-NNN |
| **nivel** | L2 |
| **fecha** | AAAA-MM-DDTHH:MM:SS-05:00 |
| **revision** | (commit SHA completo) |
| **scope** | full-repository |
| **auditor** | (identidad del auditor de seguridad) |
| **es_autor_del_cambio** | false |
| **resultado** | PASS / FAIL / PASS_WITH_OBSERVATIONS |

## Declaración de independencia

Declaro que no participé en el desarrollo de los cambios auditados. No tengo
commits en la rama auditada. No he ejecutado más de 3 auditorías L2
consecutivas sobre este scope (verificado en REGISTRO-AUDITORIAS.md).

## Resumen ejecutivo

(1-3 oraciones: alcance de seguridad evaluado, resultado, riesgos residuales)

## Controles ejecutados

| ID | Control | Resultado | Hallazgos |
|---|---|---|---|
| L2-01 | Secrets en Python/PowerShell/YAML/JSON | PASS/FAIL | |
| L2-02 | Credenciales Oracle hardcodeadas | PASS/FAIL | |
| L2-03 | Perfiles MCP sin datos sensibles | PASS/FAIL | |
| L2-04 | Variables de entorno sanitizadas | PASS/FAIL | |
| L2-05 | SQL injection patterns | PASS/FAIL | |
| L2-06 | Baseline detect-secrets actualizada | PASS/FAIL | |
| L2-07 | Dependencias sin CVE conocidas | PASS/FAIL | |
| L2-08 | Threat model vigente | PASS/FAIL | |
| L2-09 | Pre-commit hooks de seguridad activos | PASS/FAIL | |
| L2-10 | .env.example sin valores reales | PASS/FAIL | |

## Hallazgos

| ID | Severidad | Control | Descripción | Archivo | Línea | Estado |
|---|---|---|---|---|---|---|
| H-NNN | CRITICO/ALTO/MEDIO/BAJO/INFO | L2-XX | | | | ABIERTO |

## Riesgos residuales

(Riesgos que no pueden mitigarse completamente con los controles actuales.
Referencia cruzada con SECURITY-THREATS.md.)

## Conclusión

(Resultado final. Si FAIL: qué debe corregirse. Recomendaciones de seguridad.)

## Evidencia

- Comando ejecutado: `python scripts/audit_security_checklist.py --report`
- Bandit: (resultado)
- detect-secrets: (resultado)
- Hora de ejecución: (timestamp)
