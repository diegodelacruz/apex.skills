# Registro Central de Auditorías

Índice cronológico de todas las auditorías L1+ ejecutadas sobre `apex.skills`.
Cada entrada referencia el reporte completo en `governance/audit/reportes/`.

## Schema

Cada entrada debe contener:

| Campo | Descripción |
|---|---|
| `audit_id` | Identificador único: `AUD-AAAA-MMDD-L{n}-{seq}` |
| `nivel` | L1, L2, L3 o L4 |
| `fecha` | ISO 8601 con zona horaria |
| `revision` | Commit SHA auditado |
| `scope` | `full-repository` o lista de directorios/archivos |
| `auditor` | Identidad del auditor (persona o agente) |
| `es_autor` | `false` obligatorio para L1+ |
| `resultado` | `PASS`, `FAIL` o `PASS_WITH_OBSERVATIONS` |
| `hallazgos` | Cantidad total y desglose por severidad |
| `bloqueantes` | Cantidad de hallazgos CRITICO + ALTO |
| `reporte` | Ruta relativa al reporte completo |

## Verificación de rotación

Para auditorías L2+, verificar que el auditor no ha ejecutado más de 3
auditorías consecutivas sobre el mismo scope. Consultar las últimas 3 entradas
del mismo nivel y scope.

## Registro

| audit_id | nivel | fecha | revision | scope | auditor | resultado | hallazgos | reporte |
|---|---|---|---|---|---|---|---|---|
| *(vacío — se pobla con cada auditoría ejecutada)* | | | | | | | | |
