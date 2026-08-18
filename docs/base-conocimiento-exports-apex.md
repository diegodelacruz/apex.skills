# Base de conocimiento de exportes APEX

Los ZIP `apps/f109.zip` y `apps/f130.zip` son fuentes de conocimiento, no instaladores que se ejecuten automáticamente. La skill `apex-pattern-mining-safe` los lee en modo local y de solo lectura para extraer patrones reutilizables.

## Evidencia extraída y validada

| Medida | Finanzas 109 | Compras 130 |
| --- | ---: | ---: |
| Páginas YAML legibles | 194 | 173 |
| Páginas SQL | 195 | 174 |
| Esquema de parsing | DATA | DATA |
| Autoprotección de sesión | Sí | Sí |
| HTML escaping extendido | Sí | Sí |
| Deep links deshabilitados | Sí | Sí |
| Frames denegados | Sí | Sí |
| Archivos estáticos detectados | 5 | 4 |

Los dos exportes usan Universal Theme 42 y español (Ecuador). Las plantillas predominantes incluyen `Zaimella Formulario`, `Interactive Report`, `Zaimella Barra de Acciones`, `Zaimella Tabla`, formularios con título, navegación Zaimella y contenedores de pestañas.

## Patrones reutilizables

| Patrón | Decisión | Condición de reutilización |
| --- | --- | --- |
| Seguridad base: protección de sesión, escaping extendido, no deep link, no frames | Adoptar | Verificar que el requisito de negocio no justifique una excepción. |
| Universal Theme 42 y plantillas Zaimella | Adaptar | Confirmar que la aplicación objetivo tenga las plantillas y archivos estáticos requeridos. |
| Reporte interactivo con filtros y acciones | Adaptar | Definir columnas explícitas, autorización y rendimiento de la consulta. |
| Formularios Zaimella con título y barra de acciones | Adaptar | Crear IDs del nuevo destino; no copiar IDs internos. |
| Mesa de Trabajo con selector de región y refresh | Adaptar | Documentar dependencias de static IDs, regiones e items; probar cada cambio de pestaña. |
| JavaScript/CSS inline de una página existente | No copiar directamente | Extraer únicamente el propósito y rediseñar el código para el nuevo contexto. |
| SQL, paquetes y reglas de negocio de origen | No reutilizar por defecto | Usar solo con análisis funcional, de seguridad y autorización explícita. |

## Uso

```powershell
python .\skills\apex-pattern-mining-safe\scripts\mine_export_patterns.py `
  .\apps\f109.zip .\apps\f130.zip --json
```

Use el resultado como entrada de `apex-solution-design`. La secuencia recomendada para una aplicación nueva es:

1. `apex-pattern-mining-safe`
2. `apex-solution-design`
3. `apex-engineering-safe`
4. `apex-export-qa-safe`

Los repositorios remotos complementan esta base: `zaimella-skill` aporta estándares y QA; `apex-mcp` aporta el canal de herramientas MCP. Ninguno sustituye la evaluación de compatibilidad con APEX 24.1.3.
