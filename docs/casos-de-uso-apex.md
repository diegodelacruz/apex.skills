# Casos de uso para agentes Oracle APEX

Los casos son reutilizables: use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

## 1. Crear una aplicación nueva

1. Ejecute `apex-project-bootstrap-final` y cree `control-proyecto/`.
2. Registre alcance, decisiones y plan de implementación.
3. Analice los ZIP de conocimiento como patrones, sin copiar reglas de negocio ni IDs internos.
4. Diseñe en `apex-solution-design`, implemente en TEST y ejecute QA.
5. Genere scripts, release, rollback y manual Word sólo después de aprobación.

## 2. Modificar una página existente

1. Identifique aplicación, página, componente y comportamiento esperado.
2. Valide perfiles TEST/Producción en lectura.
3. Ejecute `apex-environment-alignment-complete` antes de editar.
4. Cree `control-proyecto/cambios/<id>/evidencia/environment-diff.md` con diferencias de página, región, proceso, LOV, objetos DATA y dependencias.
5. Si difieren los ambientes, recomiende sincronizar Producción hacia TEST; espere autorización. Si se rechaza, registre el baseline y el riesgo.
6. Corrija sólo en TEST, valide y prepare el release SQL/manifiesto. Producción requiere autorización separada.

## 3. Diagnosticar un error comparando TEST y Producción

Este caso es obligatorio cuando el error podría depender de versión, sesión, metadatos, objetos compilados o configuración de un ambiente.

1. Registre el síntoma reproducible: URL o aplicación/página, filtros, rol, fecha/hora, mensaje y captura si existe.
2. Conéctese con `apex-mcp-test` y `apex-mcp-production` en modo sólo lectura. Si no hay autorización de Producción, registre la limitación: un diagnóstico sólo TEST no prueba la causa en Producción.
3. Confirme en ambos ambientes la identidad exacta de aplicación/página; no infiera IDs a partir de una captura.
4. Extraiga y compare fuente efectiva de página, regiones, procesos, validaciones, items, LOVs, autorizaciones, CSS/JavaScript y objetos dependientes.
5. Para errores SQL/PLSQL, compare firma, sobrecargas, dependencias, estado de compilación y sinónimos del objeto involucrado. Use parámetros nombrados únicamente en la propuesta; no ejecute correcciones todavía.
6. Registre diferencias y evidencia en `control-proyecto/cambios/<id>/evidencia/environment-diff.md`. Clasifique cada diferencia como esperada, baseline no sincronizado o posible causa.
7. Entregue causa confirmada o hipótesis delimitada, alcance, plan de corrección TEST, validación, artefactos de promoción y rollback. No haga DDL, DML, importaciones ni despliegues durante el diagnóstico.

Prompt reutilizable:

```text
Usa apex-database-diagnostics, apex-mcp-test y apex-mcp-production.
Trabaja exclusivamente en modo sólo lectura. Confirma la identidad exacta de
la aplicación y página en ambos ambientes; compara fuente efectiva, componentes,
objetos dependientes, firma/sobrecargas y estado de compilación. Genera
control-proyecto/cambios/<id>/evidencia/environment-diff.md con evidencia,
diferencias, causa confirmada o hipótesis delimitada, plan TEST y rollback.
No ejecutes cambios.
```

## 4. Liberar un cambio aprobado

1. Compruebe QA TEST, decisiones, evidencia, release SQL y rollback.
2. Solicite autorización explícita para Producción.
3. Un operador autorizado instala los artefactos preparados; el agente registra evidencia y resultado.
4. Ejecute auditoría, cierre el plan y genere el manual Word cuando corresponda.
