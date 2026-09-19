Auditoría desacoplada independiente del ecosistema apex.skills.

ALCANCE: exclusivamente el repositorio apex.skills y sus skills. NUNCA audites proyectos del usuario ni aplicaciones APEX externas.

Este auditor es DESACOPLADO: no usa skills, orquestadores ni scripts internos del framework. El repositorio no es juez y parte.
Ejecuta tres niveles de auditoría (L1 estructura, L2 seguridad, L3 semántica) en un solo comando.

Ejecuta:

```bash
python scripts/audit_desacoplada.py
```

Opciones:
- `--level L1` / `--level L2` / `--level L3` — ejecutar solo un nivel
- `--report` — generar reportes formales en governance/audit/reportes/
- `--json` — salida JSON para integración

Interpreta el reporte:
- Cada check muestra [OK] o [!!] con su ID
- AUDIT_PASS = todo correcto, AUDIT_FAIL = hay hallazgos
- Si hay fallos, indica al usuario qué corregir y en qué archivo
- NO invoques ninguna skill del repositorio para diagnosticar o corregir
- NUNCA corrijas ni modifiques archivos como resultado de la auditoría. Solo reporta. El usuario decide qué se corrige, cuándo y cómo

Niveles:
- L1 (P01-P10): Sintaxis, tests, skills, frontmatter, enlaces, config, imports, archivos, secrets, git
- L2 (S01-S10): Secrets, Oracle creds, MCP, env vars, SQL injection, CVE, threat model, hooks
- L3 (SM01-SM10): Ejemplos, tags, routing, categorías, references, scripts, descripciones, huérfanos, frescura, consistencia README
- L4: Manual — usar plantilla governance/audit/plantillas/reporte-L4.md

User request: $ARGUMENTS
