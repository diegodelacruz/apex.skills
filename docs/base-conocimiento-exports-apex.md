# Base de conocimiento de exportes APEX

Los ZIP bajo `apps/` son fuentes locales de patrones, no instaladores ni plantillas que se copien automáticamente. `apex-pattern-mining-safe` los procesa en modo local y sólo lectura para obtener prácticas reutilizables.

## Evidencia consolidada

Los exportes de referencia contienen aplicaciones autenticadas con Universal Theme 42, esquema `DATA`, español (Ecuador), protección de estado de sesión, escaping HTML extendido, deep links deshabilitados, frames denegados y caché del navegador deshabilitada. Se identificaron patrones de formularios, reportes interactivos, barras de acciones, tablas, navegación y contenedores de pestañas.

## Reglas de reutilización

| Patrón | Decisión | Condición |
| --- | --- | --- |
| Seguridad base y protección de sesión | Adoptar | Confirmar excepciones funcionales documentadas. |
| Theme, plantillas y archivos estáticos | Adaptar | Verificar disponibilidad y compatibilidad en el destino. |
| Reportes con filtros y acciones | Adaptar | Definir columnas, autorización y rendimiento. |
| Formularios y barras de acciones | Adaptar | Crear IDs del destino; no copiar IDs internos. |
| JavaScript/CSS inline | No copiar directamente | Extraer propósito y rediseñar para el contexto destino. |
| SQL, paquetes y reglas de negocio | No reutilizar por defecto | Requiere análisis funcional, seguridad y autorización. |

Use los resultados como entrada de `apex-solution-design`; valide siempre compatibilidad con APEX 24.1.3.
