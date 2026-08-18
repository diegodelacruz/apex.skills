# Casos de uso para agentes Oracle APEX

Use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

## Regla de acceso obligatoria

El primer paso de toda solicitud que mencione TEST, Producción, Oracle, APEX, una aplicación, página u objeto es validar el perfil del ambiente solicitado con una operación de sólo lectura. Si el perfil falta, falla o no autoriza el acceso, el agente registra la limitación y no continúa ese flujo ni sustituye el ambiente sin autorización.

## 1. Inspeccionar una aplicación, página u objeto

1. Identifique ambiente, aplicación/página u objeto y propósito de la consulta.
2. Valide el perfil del ambiente solicitado en lectura.
3. Inspeccione metadatos, fuente, dependencias, compilación o definición sin ejecutar cambios.
4. Entregue evidencia, resultado y limitaciones de permisos o visibilidad.

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
4. Cree `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
5. Si difieren los ambientes, recomiende sincronizar Producción hacia TEST y espere autorización; si se rechaza, registre baseline y riesgo.
6. Corrija sólo en TEST, valide y prepare release SQL/manifiesto. Toda modificación de Producción requiere autorización explícita independiente.

## 4. Diagnosticar un error comparando TEST y Producción

1. Registre síntoma reproducible: aplicación/página, filtros, rol, fecha/hora, mensaje y captura.
2. Valide perfiles TEST y Producción en lectura. Si uno no está autorizado, declare el diagnóstico comparativo incompleto.
3. Confirme en ambos ambientes la identidad exacta de aplicación/página; no infiera IDs desde capturas.
4. Compare fuente efectiva, regiones, procesos, validaciones, items, LOVs, autorizaciones, CSS/JavaScript y objetos dependientes.
5. Para errores SQL/PLSQL, compare firma, sobrecargas, dependencias, compilación y sinónimos.
6. Registre diferencias en `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
7. Entregue causa, alcance, plan TEST, validación, artefactos y rollback. No haga cambios durante diagnóstico.

## 5. Copiar páginas de Producción a TEST

1. La solicitud nombra aplicación, páginas y autoriza explícitamente modificar TEST.
2. Valide ambos perfiles: Producción se usa sólo lectura; TEST requiere acceso autorizado para aplicar.
3. Exporte origen de Producción y genere backup recuperable del estado TEST.
4. Genere `environment-diff.md`, detalle impacto y confirme ausencia de secretos, sesiones o datos.
5. Aplique sólo el artefacto preparado en TEST, valide y registre evidencia. No modifique Producción.
6. Si falla, restaure backup TEST y registre rollback.

## 6. Copiar TEST a Producción o liberar un cambio

1. Verifique QA TEST, decisiones, evidencia, release SQL/manifiesto y rollback.
2. Solicite y registre autorización **explícita, separada y previa** para modificar Producción. Una autorización para TEST no es válida para Producción.
3. Valide el perfil autorizado de Producción en lectura antes de iniciar.
4. Un operador autorizado instala sólo los artefactos aprobados; el agente registra evidencia y resultado.
5. Si falla, ejecute el rollback aprobado. Ejecute auditoría, cierre el plan y genere el manual Word cuando corresponda.
