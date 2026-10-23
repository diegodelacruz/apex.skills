# Reglas obligatorias para agentes

Antes de modificar este repositorio, leer `docs/POLITICA-EVOLUCION-ECOSISTEMA.md`.
Para cambios Oracle/APEX, aplica la pregunta única y los modos definidos en `skills/apex/references/step-mode.md`.
Para diagnosticar un dato presente en origen y ausente o incorrecto en destino, aplica `skills/apex-database-diagnostics/references/trazabilidad-end-to-end.md`: registro testigo y de control, primera divergencia con evidencia antes de nombrar una causa, y solo lectura.

Estas reglas aplican a toda sesión y a cualquier agente que trabaje sobre
`apex.skills`. Ningún archivo puede obligar técnicamente a un agente externo
arbitrario. Su cumplimiento se refuerza mediante la política canónica,
adaptadores, hooks, CI y revisión independiente.

No uses una skill o agente mantenido dentro de este repositorio como único juez
de un cambio que lo afecte. Cuestiona y documenta la necesidad de cada skill,
agente, adaptador, ruta, dependencia, upstream o estándar agregado, modificado
o eliminado. Verifica conexiones, dependencias, estándares, pruebas, seguridad,
backups, rollback y auditoría integral antes de publicar.
