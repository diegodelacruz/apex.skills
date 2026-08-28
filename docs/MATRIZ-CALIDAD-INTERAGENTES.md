# Matriz de calidad interagentes

Esta es la línea base común para Codex, Claude, Cursor, Gemini y cualquier otro
agente que modifique el repositorio. No evalúa el estilo de respuesta del agente;
evalúa evidencia reproducible del resultado. La [política canónica](POLITICA-EVOLUCION-ECOSISTEMA.md)
tiene precedencia.

## Modelo 100/100

| Dimensión | Puntos | Evidencia mínima |
| --- | ---: | --- |
| Metadatos portables de skills | 15 | `SKILL.md`, frontmatter válido, nombre único y descubrible |
| Catálogos y documentación | 15 | inventario sincronizado y documentación sin contradicciones |
| Enlaces y conexiones | 10 | enlaces, rutas, scripts, assets y referencias resueltos |
| Gobierno, CI y hooks | 10 | política, adaptadores, hooks y CI activos |
| Independencia y gates | 15 | ningún validador interno es juez único; revisión independiente |
| Upstreams y procedencia | 10 | lock con URL, rama, commit, licencia, clasificación y propósito |
| Reproducibilidad técnica | 10 | comandos versionados, pruebas y configuración reproducibles |
| Trazabilidad del cambio | 5 | objetivo, riesgo, dependencias, rollback, evidencia y decisión |

La puntuación es informativa hasta que todos los gates obligatorios estén en
`PASS`. Un `FAIL` bloquea publicación aunque la suma sea alta; un `N/A` sólo es
válido con justificación explícita. El comando reproducible es:

```powershell
python .\scripts\audit_quality_score.py
python .\scripts\audit_quality_score.py --json
```

## Contrato para agentes

Cada agente debe descubrir primero `AGENTS.md` y esta política, declarar alcance
y riesgos, modificar sólo lo autorizado, ejecutar el auditor externo
determinístico y registrar limitaciones. El agente puede proponer una solución,
pero no puede autoaprobar un cambio de una skill o agente que él mismo haya
modificado. La revisión final debe ser humana o de un agente externo al
componente modificado.

La compatibilidad se logra por el contrato portable de `SKILL.md`; los
adaptadores específicos de cada agente son opcionales y sólo pueden añadir
integración, nunca cambiar la autoridad, los gates, los permisos ni el
significado de una skill.

## Resultado y límites

Este modelo mide controles verificables del repositorio. No sustituye pruebas
funcionales de Oracle/APEX, revisión de seguridad especializada, pruebas de
usabilidad ni aprobación de producción. Esas evidencias deben adjuntarse cuando
el cambio las afecte.
