# Plantillas de validación de paso

Cada línea siguiente es un SELECT read-only independiente y de ejemplo. Cambia los literales en mayúsculas por el objetivo real; duplica comillas simples dentro de valores de texto. Ejecuta las líneas de una validación juntas con `execute_readonly_batch`. Los SELECT de DML se observan desde otra sesión tras el commit y por eso prueban persistencia, no solo el resultado del cliente.

Los literales con acentos CP1252, por ejemplo `Descripción` o `Histórico`, son
compatibles con la ruta controlada de SQLcl en Windows. Conserva el literal
real y valida su lectura exacta; evita usar caracteres fuera de CP1252 (como
`→`) como predicados hasta contar con una ruta Unicode específica validada.

## Diccionario Oracle

```sql
select comments from all_col_comments where owner = 'DATA' and table_name = 'T_APEX_LOG' and column_name = 'DESCRIPCION'
select comments from all_tab_comments where owner = 'DATA' and table_name = 'T_APEX_LOG'
select data_type || '|' || nullable || '|' || data_length from all_tab_columns where owner = 'DATA' and table_name = 'T_APEX_LOG' and column_name = 'DESCRIPCION'
select table_name from all_tables where owner = 'DATA' and table_name = 'T_APEX_LOG'
select index_name || '|' || status from all_indexes where owner = 'DATA' and table_name = 'T_APEX_LOG' and index_name = 'T_APEX_LOG_PK'
select constraint_name || '|' || constraint_type || '|' || status from all_constraints where owner = 'DATA' and table_name = 'T_APEX_LOG' and constraint_name = 'T_APEX_LOG_PK'
select text_length from all_views where owner = 'DATA' and view_name = 'V_APEX_LOG'
select status || '|' || to_char(last_ddl_time,'YYYY-MM-DD HH24:MI:SS') from all_objects where owner = 'DATA' and object_name = 'PKG_APEX_LOG' and object_type = 'PACKAGE BODY'
select name || '|' || type || '|' || line || '|' || position || '|' || text from all_errors where owner = 'DATA' and name = 'PKG_APEX_LOG' and type = 'PACKAGE BODY' order by sequence
select status || '|' || to_char(last_ddl_time,'YYYY-MM-DD HH24:MI:SS') from all_objects where owner = 'DATA' and object_name = 'TRG_APEX_LOG_BI' and object_type = 'TRIGGER'
select sequence_name || '|' || increment_by || '|' || last_number from all_sequences where sequence_owner = 'DATA' and sequence_name = 'SEQ_APEX_LOG'
select count(*) || '|' || nvl(max(descripcion),'~NULL~') from data.t_apex_log where descripcion = 'PASO_A_PASO_EJEMPLO'
```

## Componentes APEX

En TEST, las vistas públicas verificadas para página, región, ítem, botón, proceso y acción dinámica son `APEX_APPLICATION_*`; las columnas `LAST_UPDATED_ON` y `LAST_UPDATED_BY` existen en esas vistas. La disponibilidad depende de la instalación/privilegios: si una vista no está expuesta, el paso es no verificable por esa vista, no una razón para usar `WWV_FLOW_*`.

```sql
select page_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_pages where application_id = 109 and page_id = 131
select region_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_regions where application_id = 109 and page_id = 131 and region_name = 'REGION_EJEMPLO'
select item_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_items where application_id = 109 and page_id = 131 and item_name = 'P131_EJEMPLO'
select button_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_buttons where application_id = 109 and page_id = 131 and button_name = 'GUARDAR'
select process_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_proc where application_id = 109 and page_id = 131 and process_name = 'PROCESO_EJEMPLO'
select dynamic_action_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_da where application_id = 109 and page_id = 131 and dynamic_action_name = 'ACCION_EJEMPLO'
select validation_name || '|' || to_char(last_updated_on,'YYYY-MM-DD HH24:MI:SS') || '|' || last_updated_by from apex_application_page_val where application_id = 109 and page_id = 131 and validation_name = 'VALIDACION_EJEMPLO'
```

## Evidencia TEST APEX 24.2

El conector se identifica como APEX 24.2; el diccionario expuso sinónimos públicos que resuelven a `APEX_240100` para páginas, regiones, ítems, botones, procesos, acciones dinámicas y `APEX_APPLICATION_PAGE_VAL` para validaciones. `LAST_UPDATED_ON/BY` existe en cada vista. El 2026-10-15, 17 plantillas terminaron `SUCCESS` en un lote TEST; la forma larga `APEX_APPLICATION_PAGE_VALIDATIONS` devolvió `ORA-00942` y se sustituyó por el sinónimo público `APEX_APPLICATION_PAGE_VAL`, que terminó `SUCCESS` en el lote de revalidación. No se usó Producción ni se escribieron datos.
