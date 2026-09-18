# Capacidades controladas Oracle APEX y Oracle Database

## Estado y límite

La identidad operativa es la cuenta autenticada: Oracle para objetos de base de
datos y APEX para App Builder. Ambas credenciales se guardan por separado en el
keyring. Si falta una credencial o el runner de App Builder, la operación queda
en `CONFIGURATION_REQUIRED`; no se sustituye una credencial por la otra.

## Frontera de autorización

```
cuenta Oracle o APEX autenticada -> preflight observado -> adaptador -> ambiente objetivo
```

El preflight registra cuenta, ambiente, workspace, aplicación/página u objeto y
resultado sin secretos. `AUTHORIZATION_DENIED` sólo se emite con evidencia de
Oracle o APEX de que la cuenta autenticada carece del permiso requerido.

## APEX

La única ruta admisible es App Builder con sesión autenticada y autorización
verificada, o un artefacto nativo exportado por APEX e importado mediante el
mecanismo oficial compatible con APEX 24.1.3. El preflight exige release 24.1.3,
acceso verificado a App Builder, workspace, aplicación y páginas autorizadas.

No se permite DML directo sobre `APEX_240100.WWV_FLOW_*` ni paquetes internos.
La ruta admisible para crear o modificar páginas es generar un export SQL nativo
(formato `wwv_flow_imp`) y desplegarlo mediante `scripts/Deploy-ApexPage.ps1`,
que invoca SQLcl con la conexión configurada por
`scripts/Initialize-OracleConnection.ps1`. `scripts/apex_page_generator.py` es
un constructor en memoria para generar especificaciones.

## Oracle

`scripts/controlled_capabilities.py` ejecuta DDL después de pasar preflight y
validación. Observa `session_user` y `current_schema` con la misma conexión,
exige que el objeto y esquema coincidan con la autorización verificada, valida
la gramática DDL y ejecuta la sentencia. Después verifica existencia y estado
en `ALL_OBJECTS`. Soporta `CREATE TABLE`, `ALTER TABLE` y `DROP TABLE` sobre
el objeto autorizado.

Para DDL general (vistas, índices, procedimientos, paquetes) o ejecución de
múltiples sentencias, la ruta principal es `scripts/Execute-OracleSql.ps1`
que invoca SQLcl directamente. Oracle confirma DDL implícitamente: no se
promete un rollback transaccional. Después debe comprobarse existencia y,
para PL/SQL, los errores de compilación (`SHOW ERRORS`).

## Clasificación de errores

| Código | Cuándo se emite |
| --- | --- |
| `AUTHORIZATION_DENIED` | La autorización verificada no contiene ambiente, operación o alcance. |
| `APEX_CONTEXT_INVALID` | El workspace, App Builder o esquema actual no coincide con el autorizado. |
| `ADAPTER_INCOMPATIBLE` | El release o contrato técnico no es compatible. |
| `OBJECT_CONFLICT` | La inspección real confirma que la existencia del objeto contradice la operación. |
| `EXECUTION_ERROR` | Oracle/APEX devuelve otro error; se conserva su código y mensaje. |
| `EXTERNAL_DEPENDENCY_BLOCKED` | Falta verificador de identidad, cuenta, aprobación o componente requerido. |

## Requisitos para ejecución

1. Ejecutar `scripts/Initialize-OracleConnection.ps1` con el ambiente deseado.
2. Para DDL/DML general: `scripts/Execute-OracleSql.ps1 -SqlFile <archivo.sql>`.
3. Para páginas APEX: `scripts/Deploy-ApexPage.ps1 -PageFile <export.sql> -ApplicationId <id> -Page <num>`.
4. Producción requiere `-Environment production` y aprobación explícita.
