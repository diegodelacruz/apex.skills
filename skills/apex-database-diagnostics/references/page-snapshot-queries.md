# Consultas de inspección de una página APEX

Las consultas siguientes usan las vistas públicas `APEX_APPLICATION_*`, están
en una sola línea física y aceptan únicamente los binds enteros
`:application_id` y `:page_id`. Envíalas juntas con
`execute_readonly_batch(queries, environment, bind_variables, include_identity)`;
la identidad de la sesión se incluye por defecto en la misma conexión.

## Lote para una página

```sql
select application_id, page_id, page_name, page_alias, page_mode, page_template from apex_application_pages where application_id = :application_id and page_id = :page_id
select application_id, page_id, region_id, region_name, source_type, display_sequence, display_position, parent_region_id, parent_region_name, region_source from apex_application_page_regions where application_id = :application_id and page_id = :page_id order by display_sequence
select application_id, page_id, item_id, item_name, label, display_as, display_sequence, display_position, region, item_source_type, item_source, is_required from apex_application_page_items where application_id = :application_id and page_id = :page_id order by display_sequence
select application_id, page_id, button_id, button_name, label, button_action, button_position, display_position, button_sequence, region, request_source_type from apex_application_page_buttons where application_id = :application_id and page_id = :page_id order by button_sequence
select application_id, page_id, process_id, process_name, process_type, process_point, execution_sequence, process_source, process_error_message, when_button_pressed, condition_type, condition_expression1, condition_expression2 from apex_application_page_proc where application_id = :application_id and page_id = :page_id order by execution_sequence
select application_id, page_id, validation_id, validation_name, validation_type, validation_sequence, associated_item, validation_expression1, validation_expression2, validation_failure_text, error_display_location from apex_application_page_val where application_id = :application_id and page_id = :page_id order by validation_sequence
select application_id, page_id, dynamic_action_id, dynamic_action_name, dynamic_action_sequence, when_event_name, when_element, when_region, when_button, execution_type, number_of_actions, condition_type, condition_expression1, condition_expression2 from apex_application_page_da where application_id = :application_id and page_id = :page_id order by dynamic_action_sequence
select application_id, page_id, dynamic_action_id, dynamic_action_name, action_id, action_sequence, action_name, action_pd_name, action_code, affected_elements_type, affected_elements, affected_region, affected_button, attribute_01, attribute_02, attribute_03 from apex_application_page_da_acts where application_id = :application_id and page_id = :page_id order by dynamic_action_name, action_sequence
select application_id, page_id, branch_id, branch_name, branch_action, branch_point, branch_type, process_sequence, when_button_pressed, condition_type, condition_expression1, condition_expression2 from apex_application_page_branches where application_id = :application_id and page_id = :page_id order by process_sequence
select application_id, page_id, computation_id, item_name, computation_point, execution_sequence, computation_type, computation, error_message, condition_type, condition_expression1, condition_expression2 from apex_application_page_comp where application_id = :application_id and page_id = :page_id order by execution_sequence
```

## Columnas comprobadas en TEST

Se consultaron `ALL_TAB_COLUMNS` desde una única sesión de lote de solo lectura
en TEST. Las diez vistas del lote anterior existen y contienen las columnas
seleccionadas. Para regiones, la secuencia real es `DISPLAY_SEQUENCE`; no
existen `REGION_SEQUENCE`, `REGION_TYPE` ni `REGION_SOURCE_TYPE` en esa vista.
Usa `SOURCE_TYPE` y `DISPLAY_POSITION` para esos datos. En procesos, la columna
real de orden es `EXECUTION_SEQUENCE` (no `PROCESS_SEQUENCE`). En validaciones,
el texto de error es `VALIDATION_FAILURE_TEXT` (no `ERROR_MESSAGE`). Los campos
seleccionados se verificaron para página, regiones, ítems, botones, procesos,
validaciones, acciones dinámicas, acciones de acciones dinámicas, ramas y
computaciones.

La vista de acciones instalada es `APEX_APPLICATION_PAGE_DA_ACTS`. No se
encontró `APEX_APPLICATION_PAGE_DA_ACTIONS` en `ALL_TAB_COLUMNS` de TEST.
Consulta `DA_ACTS` enlazando por `APPLICATION_ID`, `PAGE_ID` y
`DYNAMIC_ACTION_ID`.

Las columnas de fuente y condiciones ayudan a ubicar reglas asociadas al
componente; no sustituyen revisar el log APEX correspondiente cuando se
investiga un error ocurrido durante una ejecución concreta.
