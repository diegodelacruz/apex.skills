# Solicitud DBA: contexto APEX para automatización SQLcl

## Propósito

Habilitar automatización controlada de componentes APEX mediante SQLcl, sin
acceso directo a tablas `WWV_FLOW_*` ni paquetes internos de APEX.

La autorización APEX en App Builder y la identidad de una conexión Oracle
SQLcl son distintas. Tener rol de desarrollador en App Builder no garantiza que
la cuenta Oracle de SQLcl tenga un contexto de workspace válido.

## Datos que debe confirmar el DBA por ambiente

Para cada ambiente y cada workspace que se pretenda automatizar, adjuntar el
resultado de estas comprobaciones a la solicitud, sin contraseñas. Sustituir
los marcadores por el identificador de aplicación y workspace solicitados:

```sql
select application_id, application_name, workspace, owner
from apex_applications
where application_id = <APPLICATION_ID>;

select workspace_name, schema, applications
from apex_workspace_schemas
where upper(workspace_name) = upper('<WORKSPACE>')
order by schema;
```

La aplicación existente debe pertenecer al workspace solicitado y su esquema de
parsing debe estar asociado a ese workspace. La cuenta Oracle que ejecute SQLcl
debe ser también un esquema asociado al workspace o debe sustituirse por una
cuenta técnica dedicada que sí lo esté.

## Solicitud reutilizable

> Solicito habilitar la automatización SQLcl para componentes y aplicaciones
> APEX autorizadas en los workspaces indicados, en TEST y Production. Por favor
> confirme el esquema de parsing de cada aplicación existente y asocie la cuenta
> Oracle de automatización a cada workspace autorizado, o entregue una cuenta
> técnica dedicada ya asociada a dichos workspaces. La cuenta debe poder
> ejecutar una exportación nativa SQLcl de un componente existente sin
> `ORA-20987: Security Group ID invalid`.
>
> No se solicitan grants directos sobre `APEX_240100.WWV_FLOW_*`, ni ejecución
> de paquetes internos APEX, ni privilegios globales `ANY`. La automatización
> trabajará exclusivamente con exports nativos versionados, comenzando por TEST
> y verificando metadata después de cada cambio. No se autoriza automáticamente
> todo workspace: cada workspace adicional debe quedar incluido en la solicitud.

## Alcance Oracle separado

Los objetos Oracle ordinarios se resuelven por defecto en el esquema `DATA`.
Una petición que indique expresamente `DDELACRUZ.<objeto>` es la excepción.
Esta convención no cambia el usuario de sesión Oracle: los privilegios reales
los decide Oracle para la cuenta conectada.

Si la cuenta ya puede leer, crear, modificar y eliminar los objetos requeridos
en `DATA`, no se solicitan privilegios Oracle adicionales. Cualquier `ORA-01031`
que aparezca en una operación concreta se documenta y se solicita de forma
puntual, con objeto, operación, ambiente y justificación.

## Inventario automatizado del MCP

Al iniciar el trabajo en un ambiente, el MCP realiza una lectura única de:

1. Identidad de sesión SQLcl.
2. Para una aplicación existente: aplicación, workspace, esquema de parsing y
   esquemas asociados.
3. Para crear una aplicación: workspace destino y esquemas asociados, antes de
   habilitar la importación del export nativo completo.
4. Aplicaciones disponibles por workspace.

El inventario informa diferencias entre ambientes, pero no se repite por cada
petición ni bloquea la operación solicitada. Cada operación se ejecuta con las
credenciales del ambiente elegido y Oracle/APEX devuelve la autorización real.

## Secuencia de habilitación por ambiente

1. Solicitar y comprobar la asociación en TEST.
2. Ejecutar el preflight automático y una operación controlada en TEST.
3. Conservar la evidencia del resultado y corregir cualquier error de contexto
   o privilegios específicos.
4. Solo si TEST fue comprobado, solicitar la misma asociación para Production.
5. El MCP repite el preflight en Production antes de cualquier importación.

La asociación se solicita por workspace, no por aplicación individual. Una vez
asociada la cuenta Oracle a un workspace autorizado, la comprobación dinámica
cubre sus aplicaciones existentes. Un workspace nuevo requiere una solicitud
nueva y explícita.
