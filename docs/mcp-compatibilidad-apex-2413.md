# Compatibilidad global del MCP con APEX 24.1.3

## Evidencia de Producción

La conexión MCP de Producción y el perfil seguro validan correctamente. La base
reporta APEX `24.1.3` y el diccionario interno corresponde al propietario
`APEX_240100`.

El upstream actual de `apex-mcp` está acoplado a otra forma del diccionario:

- consulta `WWV_FLOW_PAGE_PLUGS` sin propietario;
- espera `NAME` y `DISPLAY_SEQUENCE` donde APEX 24.1.3 expone
  `REGION_NAME` y `PLUG_DISPLAY_SEQUENCE`;
- consulta `PARENT_REGION`, pero la vista expone `PARENT_REGION_ID` y
  `PARENT_REGION_NAME`;
- consulta `CSS_INLINE`, que no existe en la vista de páginas de este entorno.

Esto produce `ORA-00942` y `ORA-00904` en varias herramientas, no solamente en
`apex_update_region`.

## Solución global implementada en el adaptador

El parche canónico `scripts/Apply-ApexMcpApex241CompatibilityPatch.py` se
aplica automáticamente durante la inicialización y cubre las rutas del
upstream que inspeccionan o mutan páginas existentes:

1. Las lecturas usan vistas públicas `APEX_APPLICATION_*` y las columnas
   incompatibles se adaptan (`CSS_INLINE`, `PARENT_REGION` y opciones de
   plantilla).
2. Lecturas, modificaciones, copias y eliminaciones que aún requieren tablas
   internas usan `APEX_240100.WWV_FLOW_*` y los nombres reales de 24.1.3.
3. Las operaciones de creación y componentes nuevos conservan las APIs de
   importación `WWV_FLOW_IMP*`/`WWV_FLOW_IMP_PAGE` del upstream.
4. El comprobador de permisos y el script de grants generan referencias al
   propietario correcto.
5. El inicializador ejecuta también
   `scripts/Validate-ApexMcpApex241Compatibility.py`.
6. Ejecutar un preflight de capacidades antes de exponer herramientas mutantes:
   versión, propietario, vistas, paquetes, `EXECUTE`, workspace y aplicación.
7. Añadir pruebas de contrato para páginas, regiones, items, botones, procesos,
   acciones dinámicas, LOVs, copias y eliminaciones.

## Permisos requeridos

La cuenta de Producción debe tener los permisos de ejecución sobre las APIs de
APEX necesarias para el workspace y esquema objetivo. No se debe conceder un
`UPDATE` general sobre tablas internas como sustituto de la compatibilidad.

La explicación operativa y el texto listo para enviar al DBA están en
[Solicitud de permisos DBA para APEX 24.1.3](SOLICITUD-PERMISOS-DBA-APEX-2413.md).

Un `GRANT UPDATE ON APEX_240100.WWV_FLOW_PAGE_PLUGS` podría eliminar el primer
`ORA-00942`, pero no resolvería los nombres de columnas incompatibles ni las
restantes herramientas. Además, el DML directo evita validaciones de APEX.

## Estado operativo

La validación estática del adaptador pasa. Eso no equivale a privilegios Oracle:
en la Producción revisada el usuario todavía no tiene los grants DML sobre las
tablas internas. Por tanto, las creaciones vía APIs con `EXECUTE` pueden estar
disponibles, pero las modificaciones/eliminaciones de componentes existentes
seguirán devolviendo `ORA-01031` hasta que el DBA otorgue los permisos exactos
al usuario del perfil. El MCP no puede concederlos por sí mismo.

## Criterio de finalización

La capacidad se considerará habilitada únicamente cuando el mismo adaptador
compatible pase, en TEST y después en Producción, pruebas controladas de:

- leer una aplicación y una página;
- crear una página;
- agregar y modificar una región, item, botón y proceso;
- copiar una página;
- eliminar un componente de prueba;
- exportar y validar la aplicación;
- confirmar rollback o eliminación de la prueba.
