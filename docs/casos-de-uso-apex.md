# Casos de uso para agentes Oracle APEX

Los casos son reutilizables: use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

## Regla de acceso obligatoria

El primer paso de toda solicitud que mencione TEST, Producción, Oracle, APEX, una aplicación, página u objeto es validar el perfil del ambiente solicitado con una operación de sólo lectura. Si el perfil falta, falla o no autoriza el acceso, el agente registra la limitación y no continúa ese flujo ni sustituye el ambiente sin autorización.

## 1. Inspeccionar una aplicación, página u objeto

1. Identifique ambiente, aplicación/página u objeto y propósito de la consulta.
2. Valide el perfil del ambiente solicitado en lectura.
3. Inspeccione metadatos, fuente, dependencias, compilación o definición del objeto sin ejecutar cambios.
4. Entregue evidencia, resultado y cualquier limitación de permisos o visibilidad.

## 2. Crear una aplicación nueva

1. Ejecute `apex-project-bootstrap-final` y cree `control-proyecto/`.
2. Registre alcance, decisiones y plan de implementación.
3. Analice los ZIP de conocimiento como patrones, sin copiar reglas de negocio ni IDs internos.
4. Diseñe en `apex-solution-design`, implemente en TEST y ejecute QA.
5. Genere scripts, release, rollback y manual Word sólo después de aprobación.

## 3. Modificar una página existente

1. Identifique aplicación, página, componente y comportamiento esperado.
2. Valide perfiles TEST/Producción en lectura.
3. Ejecute `apex-environment-alignment-complete` antes de editar.
4. Cree `control-proyecto/cambios/<id>/evidencia/environment-diff.md` con diferencias de página, región, proceso, LOV, objetos DATA y dependencias.
5. Si difieren los ambientes, recomiende sincronizar Producción hacia TEST; espere autorización. Si se rechaza, registre el baseline y el riesgo.
6. Corrija sólo en TEST, valide y prepare el release SQL/manifiesto. Producción requiere autorización separada.

## 4. Diagnosticar un error comparando TEST y Producción

1. Registre el síntoma reproducible: aplicación/página, filtros, rol, fecha/hora, mensaje y captura si existe.
2. Valide los perfiles TEST y Producción en lectura. Si uno no está autorizado, declare que el diagnóstico comparativo es incompleto.
3. Confirme en ambos ambientes la identidad exacta de aplicación/página; no infiera IDs a partir de una captura.
4. Extraiga y compare fuente efectiva de página, regiones, procesos, validaciones, items, LOVs, autorizaciones, CSS/JavaScript y objetos dependientes.
5. Para errores SQL/PLSQL, compare firma, sobrecargas, dependencias, estado de compilación y sinónimos del objeto involucrado.
6. Registre diferencias en `control-proyecto/cambios/<id>/evidencia/environment-diff.md`; clasifíquelas como esperadas, baseline no sincronizado o posible causa.
7. Entregue causa confirmada o hipótesis delimitada, alcance, plan TEST, validación, artefactos de promoción y rollback. No haga DDL, DML, importaciones ni despliegues durante el diagnóstico.

## 5. Copiar páginas de Producción a TEST

1. La solicitud debe nombrar aplicación, páginas y autorizar explícitamente la modificación de TEST.
2. Valide ambos perfiles: Producción se usa sólo en lectura; TEST requiere acceso autorizado para aplicar el cambio.
3. Exporte la página o aplicación origen de Producción y genere backup/export recuperable del estado actual de TEST.
4. Genere `environment-diff.md`, detalle componentes afectados y confirme que la copia no incluye secretos, sesiones ni datos.
5. Aplique únicamente el artefacto preparado en TEST, valide la copia y registre evidencia. No modifique Producción.
6. Si falla, restaure el backup de TEST y registre el rollback. Prepare los scripts TEST para una liberación posterior autorizada.

## 6. Liberar un cambio aprobado

1. Compruebe QA TEST, decisiones, evidencia, release SQL y rollback.
2. Solicite autorización explícita para Producción.
3. Un operador autorizado instala los artefactos preparados; el agente registra evidencia y resultado.
4. Ejecute auditoría, cierre el plan y genere el manual Word cuando corresponda.
