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

No se permite DML sobre `APEX_240100.WWV_FLOW_*`, `WWV_FLOW_IMP*` ni paquetes
internos. `scripts/apex_page_generator.py` es únicamente un constructor en
memoria. `scripts/apex_rest_client.py` se conserva para compatibilidad de
importación, pero su transporte era simulado y ahora responde
`ADAPTER_INCOMPATIBLE` para toda operación.

## Oracle

`scripts/controlled_capabilities.py` separa el preflight de la ejecución. Antes
de DDL observa `session_user` y `current_schema` con la misma conexión y exige
que el objeto y esquema coincidan con la autorización verificada. En su primer
contrato soporta una sola sentencia `CREATE TABLE`, `ALTER TABLE` o `DROP TABLE`
sobre el objeto explícitamente autorizado. No ofrece grants y no presupone
privilegios.

Antes de invocar una ejecución real, la integración debe registrar el DDL actual,
existencia, dependencias, privilegio efectivo, cuota cuando aplique y plan de
reversión compensatoria. Oracle confirma DDL implícitamente: no se promete un
rollback transaccional. Después debe comprobarse existencia y, para PL/SQL, los
errores de compilación.

## Clasificación de errores

| Código | Cuándo se emite |
| --- | --- |
| `AUTHORIZATION_DENIED` | La autorización verificada no contiene ambiente, operación o alcance. |
| `APEX_CONTEXT_INVALID` | El workspace, App Builder o esquema actual no coincide con el autorizado. |
| `ADAPTER_INCOMPATIBLE` | El release o contrato técnico no es compatible. |
| `OBJECT_CONFLICT` | La inspección real confirma que la existencia del objeto contradice la operación. |
| `EXECUTION_ERROR` | Oracle/APEX devuelve otro error; se conserva su código y mensaje. |
| `EXTERNAL_DEPENDENCY_BLOCKED` | Falta verificador de identidad, cuenta, aprobación o componente requerido. |

## Prueba TEST pendiente

La aceptación exige una autorización escrita que identifique: ambiente TEST,
cuenta/identidad, workspace, aplicación y página temporal, objeto temporal y
operaciones permitidas. Sólo entonces se podrá ejecutar una mutación mínima,
prueba negativa, validación posterior y limpieza compensatoria. Producción no
forma parte de esa autorización.
