# Solicitud de permisos DBA para MCP y Oracle APEX 24.1.3

> **RETIRADA — NO EJECUTAR.** Este documento histórico propone grants sobre
> `WWV_FLOW_*` y `WWV_FLOW_IMP*`, que no son una vía aprobada. No solicite ni
> ejecute sus sentencias; consulte `CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`.

## Objetivo

Habilitar una cuenta técnica Oracle dedicada exclusivamente al MCP para leer,
crear, modificar, copiar y eliminar componentes APEX de las aplicaciones
autorizadas, usando la instalación APEX `24.1.3`, cuyo propietario de
diccionario validado es `APEX_240100`. `DDELACRUZ` es un marcador de posición:
solo puede mantenerse si identifica esa cuenta técnica dedicada, no una cuenta
personal ni compartida.

El `workspace_id`, el nombre del workspace y el esquema se envían desde el
perfil seguro MCP. Esos datos seleccionan el contexto APEX, pero no conceden
privilegios Oracle ni aplican aislamiento por filas. En particular, un grant
sobre una tabla `WWV_FLOW_*` habilita el objeto completo, no solo un workspace
o una aplicación. Los grants siguientes solo pueden habilitarse junto con los
controles compensatorios indicados en esta solicitud.

## Sentencias para revisión y ejecución DBA

El DBA debe revisar el alcance, sustituir `DDELACRUZ` si corresponde y ejecutar
las sentencias con una cuenta propietaria o administrativa autorizada.

### Condiciones obligatorias de alcance y revocación

Antes de conceder DML sobre `WWV_FLOW_*`, el responsable de seguridad debe
aprobar por escrito estas condiciones:

- usar una cuenta MCP técnica, exclusiva y sin uso interactivo humano;
- configurar y verificar en el adaptador una allowlist exigible de aplicaciones
  y páginas autorizadas; el perfil MCP por sí solo no sustituye ese control;
- mantener el secreto de la cuenta fuera del repositorio y restringir su uso al
  servicio MCP autorizado;
- registrar el ticket de cambio, el periodo de vigencia y el responsable de
  revocar los permisos cuando termine la intervención; y
- no conceder estos DML si se requiere aislamiento Oracle estricto por
  workspace o aplicación. En ese caso debe usarse una API controlada que
  compruebe ese alcance o un entorno separado.

### APIs APEX para creación, importación, copia y contexto

```sql
grant execute on APEX_240100.APEX_UTIL
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_IMP
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_IMP_SHARED
    to DDELACRUZ;

grant execute on APEX_240100.WWV_IMP_WORKSPACE
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_IMP_PAGE
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_COPY
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_UTILITIES
    to DDELACRUZ;

grant execute on APEX_240100.WWV_FLOW_PAGE_DEV
    to DDELACRUZ;
```

### Lectura adicional

En la conexión revisada faltaba lectura directa del catálogo de LOVs:

```sql
grant select on APEX_240100.APEX_APPLICATION_LOV
    to DDELACRUZ;
```

### Modificación de componentes existentes

```sql
grant select, update, delete on APEX_240100.WWV_FLOW_PAGE_PLUGS
    to DDELACRUZ;

grant select, update, delete on APEX_240100.WWV_FLOW_STEP_ITEMS
    to DDELACRUZ;

grant select, update, delete on APEX_240100.WWV_FLOW_STEPS
    to DDELACRUZ;
```

### Eliminación en cascada de componentes de una página

Estas tablas se requieren únicamente para la ruta de eliminación en cascada
del adaptador cuando la API interna de borrado no está disponible:

```sql
grant delete on APEX_240100.WWV_FLOW_STEP_PROCESSING
    to DDELACRUZ;

grant select, delete on APEX_240100.WWV_FLOW_STEP_BUTTONS
    to DDELACRUZ;

grant delete on APEX_240100.WWV_FLOW_STEP_DA_ACTIONS
    to DDELACRUZ;

grant delete on APEX_240100.WWV_FLOW_STEP_DA_EVENTS
    to DDELACRUZ;

grant delete on APEX_240100.WWV_FLOW_PAGE_COMPUTATIONS
    to DDELACRUZ;

grant delete on APEX_240100.WWV_FLOW_STEP_VALIDATIONS
    to DDELACRUZ;
```

## Qué significa la advertencia sobre `WWV_FLOW_*`

`WWV_FLOW_*` son objetos internos que APEX utiliza para guardar su metadata.
No son una API pública estable como las vistas `APEX_APPLICATION_*` ni como
las APIs documentadas del App Builder.

En este adaptador se usan porque APEX 24.1.3 no expone una API pública completa
para modificar todos los componentes de una página existente. Por ejemplo,
`WWV_FLOW_PAGE_PLUGS` contiene las regiones y `WWV_FLOW_STEP_ITEMS` contiene
los items.

Un `update` o `delete` directo sobre esas tablas puede cambiar la metadata sin
que el App Builder ejecute todas sus validaciones de interfaz, dependencias,
identificadores, componentes hijos o consistencia funcional. Por eso:

- el DBA debe aprobar expresamente esos grants;
- se debe respaldar o exportar la aplicación antes de mutar Producción;
- se debe probar primero en TEST;
- cada cambio debe tener alcance, evidencia y rollback;
- después de la operación se debe validar la aplicación en App Builder;
- el permiso debe concederse directamente a la cuenta técnica MCP, no mediante
  un rol administrativo amplio;
- la allowlist de aplicaciones y páginas debe verificarse antes de cada cambio;
  y
- el responsable del cambio debe revocar los DML internos al cerrar la ventana
  autorizada, salvo una excepción de vigencia aprobada y documentada.

La advertencia no significa que los grants sean incorrectos ni que el MCP no
pueda usarlos. Significa que habilitan una ruta técnica de bajo nivel, con
alcance de objeto completo, que debe operarse con control de cambios y controles
compensatorios verificables.

## Privilegios que no deben concederse

No es necesario ni recomendable conceder:

```text
DBA
GRANT ANY PRIVILEGE
GRANT ANY OBJECT PRIVILEGE
UPDATE ANY TABLE
DELETE ANY TABLE
SELECT ANY DICTIONARY
```

Tampoco se debe conceder acceso indiscriminado a todas las tablas cuyo nombre
empiece por `WWV_FLOW_`. La solicitud está limitada a los objetos y operaciones
enumerados arriba.

## Validación posterior del DBA

```sql
select privilege, owner, table_name
from user_tab_privs
where owner = 'APEX_240100'
  and table_name in (
    'APEX_UTIL',
    'WWV_FLOW_IMP',
    'WWV_FLOW_IMP_SHARED',
    'WWV_IMP_WORKSPACE',
    'WWV_FLOW_IMP_PAGE',
    'WWV_FLOW_COPY',
    'WWV_FLOW_UTILITIES',
    'WWV_FLOW_PAGE_DEV',
    'APEX_APPLICATION_LOV',
    'WWV_FLOW_PAGE_PLUGS',
    'WWV_FLOW_STEP_ITEMS',
    'WWV_FLOW_STEPS',
    'WWV_FLOW_STEP_PROCESSING',
    'WWV_FLOW_STEP_BUTTONS',
    'WWV_FLOW_STEP_DA_ACTIONS',
    'WWV_FLOW_STEP_DA_EVENTS',
    'WWV_FLOW_PAGE_COMPUTATIONS',
    'WWV_FLOW_STEP_VALIDATIONS'
)
order by table_name, privilege;
```

El resultado debe conservarse como evidencia de la solicitud aprobada. Luego
se debe reiniciar una tarea MCP nueva y ejecutar primero una prueba de lectura,
seguida de una prueba controlada de escritura en TEST.

Al cerrar la ventana de cambio, el DBA debe comprobar la revocación de los DML
internos con la misma consulta y adjuntar el resultado al ticket. Si una
excepción aprobada conserva permisos, debe documentar su vigencia, justificativo
y la próxima fecha de revisión.

## Referencias relacionadas

- [Compatibilidad global APEX 24.1.3](mcp-compatibilidad-apex-2413.md)

- [Auditoría integral del repositorio](AUDITORIA-INTEGRAL-2026-09-01.md)
