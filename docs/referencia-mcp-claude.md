# Hallazgos de la revisión del repositorio `mcp`

## Qué hace diferente

El repositorio local `D:\Users\ddelacruz\Desktop\Python\codex\mcp` es un
administrador de perfiles y procesos. Su parche `apex_mcp_patch` reemplaza la
conexión ADB con una conexión Oracle directa mediante Easy Connect y luego
ejecuta el servidor `apex-mcp` sin introducir un modo de solo lectura propio.

El proceso inyecta en memoria las variables `ORACLE_DB_USER`, `ORACLE_DB_PASS`,
`ORACLE_DSN`, `APEX_WORKSPACE_ID`, `APEX_SCHEMA` y `APEX_WORKSPACE_NAME`, y
Claude recibe directamente el servidor `apex-mcp` por `stdio`.

## Qué puede explicar el éxito con Claude

El servidor genera páginas y componentes nuevos usando llamadas PL/SQL de
`wwv_flow_imp_page`. Ese camino puede funcionar con los permisos de ejecución
que ya tiene el usuario, incluso cuando las herramientas de edición de
componentes existentes fallan.

El repositorio no resuelve el problema observado en APEX 24.1.3:

- no contiene un adaptador de diccionario APEX por versión;
- no corrige `WWV_FLOW_PAGE_PLUGS` frente a `APEX_240100`;
- no corrige `NAME` frente a `REGION_NAME` ni
  `DISPLAY_SEQUENCE` frente a `PLUG_DISPLAY_SEQUENCE`;
- no proporciona una implementación general de actualización/eliminación de
  páginas y componentes.

## Qué aprovecharemos

1. El patrón de conexión directa y variables inyectadas en memoria.
2. El reinicio del proceso MCP cuando cambia el perfil o la red.
3. El uso del servidor MCP original para operaciones de creación basadas en
   `wwv_flow_imp_page`.
4. La separación entre perfiles TEST y Producción.

No se copiará código del repositorio. Nuestro MCP conservará el keyring y el
registro Codex, pero incorporará una capa propia de compatibilidad APEX 24.1.3.

## Conclusión

El repositorio `mcp` explica por qué Claude pudo crear una página, pero no
elimina el `ORA-00942` ni habilita por sí mismo la edición completa. El cambio
necesario sigue siendo adaptar el servidor MCP para que detecte la versión y
use el diccionario/API correspondiente para cada familia de componentes.
