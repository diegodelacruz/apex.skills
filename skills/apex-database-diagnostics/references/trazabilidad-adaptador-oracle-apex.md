# Adaptador Oracle/APEX para Trazabilidad End-to-End

Este adaptador traduce [la metodología TE2E](trazabilidad-end-to-end.md) a sondas
de solo lectura para Oracle Database y Oracle APEX. No agrega reglas: el
contrato, los estados, la taxonomía y los criterios de cierre son los del
núcleo. Si una sonda de este archivo no aplica al flujo real, se descarta. El
flujo no se adapta a la sonda.

## Uso

- Envía las sondas de una ronda juntas con
  `apex-controlled-mcp.execute_readonly_batch` (como máximo 25 SELECT, una sola
  sesión de solo lectura, con identidad incluida). Usa `execute_readonly_query`
  para una sola sonda.
- La ruta controlada admite solo binds enteros. `:application_id` y `:page_id`
  van como binds y los nombres de objetos como literales: cambia los literales
  en mayúsculas (`'DATA'`, `'T_OBJETO_EJEMPLO'`, …) por el objeto real y
  duplica las comillas simples dentro de los valores de texto.
- Cada sonda está en una sola línea física, sin comentarios ni `;`, y lleva un
  límite de filas o un predicado por llave.
- En `LIKE`, `_` es comodín. Si el nombre buscado lo contiene, el resultado
  puede traer coincidencias de más: confírmalas por nombre exacto.
- Usa las vistas públicas `APEX_APPLICATION_*`, `APEX_APPL_*` y
  `APEX_WORKSPACE_*`. No consultes `WWV_FLOW_*`.
- Si una vista no está expuesta para la credencial, la etapa queda
  `NO_OBSERVABLE` por esa vía. No es una razón para ampliar la búsqueda.

## Etapa de presentación (APEX)

Primero toma la fuente de cada región, sus ítems, procesos y computaciones con
el lote de [consultas de snapshot de página](page-snapshot-queries.md). Después,
para buscar lo que oculta un registro en la pantalla, usa:

```sql
select page_id || '|' || region_id || '|' || region_name || '|' || source_type from apex_application_page_regions where application_id = :application_id and upper(dbms_lob.substr(region_source, 4000, 1)) like '%V_OBJETO_EJEMPLO%' fetch first 50 rows only
select region_id || '|' || region_name || '|' || source_type || '|' || condition_type || '|' || condition_expression1 || '|' || condition_expression2 || '|' || authorization_scheme from apex_application_page_regions where application_id = :application_id and page_id = :page_id order by display_sequence
select interactive_report_id || '|' || region_id || '|' || region_name || '|' || max_row_count || '|' || max_rows_per_page || '|' || page_items_to_submit from apex_application_page_ir where application_id = :application_id and page_id = :page_id
select r.region_id || '|' || r.report_id || '|' || r.application_user || '|' || r.report_name || '|' || r.report_type || '|' || r.status || '|' || c.condition_type || '|' || c.condition_column_name || '|' || c.condition_operator || '|' || c.condition_expression || '|' || c.condition_expression2 || '|' || c.condition_enabled from apex_application_page_ir_rpt r left join apex_application_page_ir_cond c on c.application_id = r.application_id and c.report_id = r.report_id where r.application_id = :application_id and r.page_id = :page_id fetch first 100 rows only
select to_char(view_date,'YYYY-MM-DD HH24:MI:SS') || '|' || apex_user || '|' || rows_queried || '|' || ir_saved_report_id || '|' || ir_search || '|' || regions_from_cache || '|' || error_message from apex_workspace_activity_log where application_id = :application_id and page_id = :page_id and view_date >= sysdate - 1 order by view_date desc fetch first 20 rows only
select to_char(message_timestamp,'YYYY-MM-DD HH24:MI:SS') || '|' || page_view_id || '|' || message_level || '|' || substr(message,1,300) from apex_debug_messages where application_id = :application_id and page_id = :page_id and message_timestamp >= systimestamp - interval '1' hour order by message_timestamp desc fetch first 50 rows only
```

La primera consulta responde la pregunta inversa: qué regiones de una
aplicación leen un objeto. Siempre se acota por `:application_id` y solo
examina los primeros 4000 caracteres de cada fuente.

Pistas de `D5 CONSOLIDADO_NO_VISIBLE` en APEX:

- condiciones y esquemas de autorización de la región;
- ítems de página con valor por defecto o en estado de sesión;
- filtros de reportes interactivos guardados, públicos o del propio usuario
  (`application_user`);
- límites de filas y paginación;
- regiones servidas desde caché (`regions_from_cache`);
- `rows_queried` de la vista de página que reproduce el síntoma.

El log de depuración solo existe si la depuración estaba activa en esa vista
de página. Si está vacío, la etapa no queda `AUSENTE`, sino `NO_OBSERVABLE`
por esa vía.

## Procesos asíncronos (APEX y Scheduler)

```sql
select automation_id || '|' || name || '|' || trigger_type || '|' || polling_status || '|' || to_char(polling_last_run_timestamp,'YYYY-MM-DD HH24:MI:SS') || '|' || to_char(polling_next_run_timestamp,'YYYY-MM-DD HH24:MI:SS') || '|' || query_type || '|' || table_owner || '.' || table_name || '|' || substr(where_clause,1,300) from apex_appl_automations where application_id = :application_id
select automation_name || '|' || status || '|' || to_char(start_timestamp,'YYYY-MM-DD HH24:MI:SS') || '|' || to_char(end_timestamp,'YYYY-MM-DD HH24:MI:SS') || '|' || successful_row_count || '|' || error_row_count from apex_automation_log where application_id = :application_id and start_timestamp >= systimestamp - interval '7' day order by start_timestamp desc fetch first 20 rows only
select owner || '.' || job_name || '|' || job_type || '|' || enabled || '|' || state || '|' || to_char(last_start_date,'YYYY-MM-DD HH24:MI:SS') || '|' || to_char(next_run_date,'YYYY-MM-DD HH24:MI:SS') || '|' || repeat_interval || '|' || failure_count from all_scheduler_jobs where owner = 'DATA' and upper(job_action) like '%PKG_OBJETO_EJEMPLO%' fetch first 20 rows only
select job_name || '|' || status || '|' || to_char(actual_start_date,'YYYY-MM-DD HH24:MI:SS') || '|' || run_duration || '|' || error# || '|' || substr(errors,1,300) from all_scheduler_job_run_details where owner = 'DATA' and job_name = 'JOB_OBJETO_EJEMPLO' and log_date >= systimestamp - interval '7' day order by log_date desc fetch first 10 rows only
select mview_name || '|' || refresh_mode || '|' || refresh_method || '|' || to_char(last_refresh_date,'YYYY-MM-DD HH24:MI:SS') || '|' || staleness || '|' || compile_state from all_mviews where owner = 'DATA' and mview_name = 'MV_OBJETO_EJEMPLO'
```

Antes de declarar `AUSENTE` en una etapa asíncrona, compara el momento del
testigo con la última ejecución terminada. Si no terminó, el estado es
`PENDIENTE` (`D7`).

## Descubrimiento en el diccionario Oracle

```sql
select referenced_owner || '.' || referenced_name || '|' || referenced_type || '|' || dependency_type from all_dependencies where owner = 'DATA' and name = 'V_OBJETO_EJEMPLO' and referenced_owner not in ('SYS', 'PUBLIC') fetch first 100 rows only
select owner || '.' || name || '|' || type from all_dependencies where referenced_owner = 'DATA' and referenced_name = 'T_OBJETO_EJEMPLO' fetch first 100 rows only
select text_length || '|' || text_vc from all_views where owner = 'DATA' and view_name = 'V_OBJETO_EJEMPLO'
select name || '|' || type || '|' || line || '|' || trim(text) from all_source where owner = 'DATA' and name = 'PKG_OBJETO_EJEMPLO' and type = 'PACKAGE BODY' and upper(text) like '%T_OBJETO_EJEMPLO%' order by line fetch first 100 rows only
select trigger_name || '|' || trigger_type || '|' || triggering_event || '|' || status || '|' || when_clause from all_triggers where table_owner = 'DATA' and table_name = 'T_OBJETO_EJEMPLO'
select object_type || '|' || status || '|' || to_char(last_ddl_time,'YYYY-MM-DD HH24:MI:SS') from all_objects where owner = 'DATA' and object_name = 'PKG_OBJETO_EJEMPLO'
```

- **Hacia atrás:** la primera consulta indica qué usa una vista o un
  programa.
- **Hacia adelante y escritores:** la segunda indica quién depende de una
  tabla. Busca las líneas concretas con `ALL_SOURCE` solo en los objetos que
  devuelva, nunca en todo el esquema.
- `TEXT_VC` trunca en 4000 caracteres. Si `TEXT_LENGTH` es mayor, la
  definición está incompleta por esa vía y hay que obtenerla desde un export.
- `ALL_DEPENDENCIES` no ve el SQL dinámico. Si el código arma sentencias en
  tiempo de ejecución, la etapa se descubre leyendo ese código.
- `LAST_DDL_TIME` y `STATUS` muestran la versión desplegada. Compáralos con el
  repositorio antes de razonar sobre el código.

## Sondas del testigo (plantillas)

Estas formas se completan con los objetos del mapa. No se ejecutan tal cual:

```text
presencia      : select <llave> || '|' || <atr_1> || '|' || <atr_2> from <OWNER>.<TABLA_ETAPA> where <llave> in (<testigo>, <control>) fetch first 10 rows only
condición      : select <llave> || '|' || case when <condición copiada de la etapa> then 'PASA' else 'EXCLUIDO' end from <OWNER>.<FUENTE_ETAPA> where <llave> in (<testigo>, <control>)
transformación : select <llave> || '|' || <valor_entrada> || '|' || <expresión copiada de la etapa> from <OWNER>.<ENTRADA_ETAPA> where <llave> in (<testigo>, <control>)
agregado       : select sum(<medida>) || '|' || count(*) from <OWNER>.<DETALLE> where <llave_grupo> = <grupo_del_testigo>
contrapartida  : select <llave> || '|' || <medida> from <OWNER>.<DETALLE> where <llave_grupo> = <grupo_del_testigo> and <medida> = -<valor_testigo> fetch first 10 rows only
dato pasado    : select <llave> || '|' || <valor> from <OWNER>.<TABLA> as of timestamp systimestamp - interval '<n>' minute where <llave> = <testigo>
```

- Los conteos y las sumas solo se permiten acotados al grupo del testigo.
- Los ítems de página (`:P<n>_…`) de la fuente de una región no son binds de
  la ruta controlada, y el estado de sesión del usuario no se puede leer.
  Para evaluar el predicado, reemplázalos por los literales que usó quien
  observó el síntoma, o decláralos como supuesto.
- Califica los objetos con el propietario que devuelve `ALL_DEPENDENCIES`
  (`referenced_owner`). Un nombre sin calificar que funciona dentro de una
  vista puede dar `ORA-00942` en la sesión de diagnóstico; eso deja la sonda
  `NO_OBSERVABLE` por esa vía, no la etapa `AUSENTE`.
- La consulta "dato pasado" (flashback) depende de la retención de undo y
  del privilegio. Si falla, la etapa queda `NO_OBSERVABLE` para ese momento.
- La lógica copiada de la etapa debe ser la versión desplegada, no la del
  repositorio.

## Columnas comprobadas en TEST

El 2026-10-23 se consultó `ALL_TAB_COLUMNS` en TEST (APEX 24.1.3) desde un
lote de solo lectura. Existen todas las columnas usadas arriba en
`ALL_DEPENDENCIES`, `ALL_VIEWS` (`TEXT_VC`), `ALL_SOURCE`, `ALL_TRIGGERS`,
`ALL_SCHEDULER_JOBS`, `ALL_SCHEDULER_JOB_RUN_DETAILS`, `ALL_MVIEWS`,
`ALL_OBJECTS`, `APEX_APPLICATION_PAGE_IR`, `APEX_APPLICATION_PAGE_IR_RPT`,
`APEX_APPLICATION_PAGE_IR_COND`, `APEX_APPL_AUTOMATIONS`, `APEX_AUTOMATION_LOG`,
`APEX_WORKSPACE_ACTIVITY_LOG` y `APEX_DEBUG_MESSAGES`. La instalación expone
vistas de dos esquemas APEX, de modo que los nombres de columna aparecen
repetidos en el diccionario. Las sondas usan los sinónimos públicos.
