# Casos de uso para agentes Oracle APEX

Use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

## Regla de acceso obligatoria

El primer paso de toda solicitud que mencione TEST, Producción, Oracle, APEX, una aplicación, página u objeto es validar el perfil del ambiente solicitado con una operación de sólo lectura. Si el perfil falta, falla o no autoriza el acceso, el agente registra la limitación y no continúa ese flujo ni sustituye el ambiente sin autorización.

## 1. Inspeccionar una aplicación, página u objeto

1. Identifique ambiente, aplicación/página u objeto y propósito.
2. Valide el perfil solicitado en lectura.
3. Inspeccione metadatos, fuente, dependencias, compilación o definición sin cambios.
4. Entregue evidencia, resultado y limitaciones.

## 2. Crear una aplicación nueva

1. Ejecute `apex-project-bootstrap-final` y cree `control-proyecto/`.
2. Registre alcance, decisiones y plan.
3. Analice ZIP de conocimiento como patrones; no copie reglas de negocio ni IDs.
4. Diseñe, implemente en TEST y ejecute QA según alcance.
5. Genere scripts, release, rollback y manual Word cuando correspondan.

## 3. Modificar una página existente

1. Identifique aplicación, página, componente y comportamiento esperado.
2. Valide perfiles TEST/Producción en lectura.
3. Ejecute `apex-environment-alignment-complete` antes de editar.
4. Cree `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
5. Si difieren los ambientes, recomiende sincronizar Producción hacia TEST y espere autorización; si se rechaza, registre baseline y riesgo.
6. Corrija en TEST y prepare sólo los controles y artefactos proporcionales al alcance. Para modificar Producción, solicite aprobación explícita independiente.

## 4. Diagnosticar un error comparando TEST y Producción

1. Registre síntoma reproducible: aplicación/página, filtros, rol, fecha/hora, mensaje y captura.
2. Valide perfiles TEST y Producción en lectura. Si uno no está autorizado, declare el diagnóstico comparativo incompleto.
3. Confirme identidad exacta en ambos ambientes; no infiera IDs desde capturas.
4. Compare fuente efectiva, regiones, procesos, validaciones, items, LOVs, autorizaciones, CSS/JavaScript y objetos dependientes.
5. Para errores SQL/PLSQL, compare firma, sobrecargas, dependencias, compilación y sinónimos.
6. Registre diferencias en `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
7. Entregue causa, alcance, plan TEST, validación y rollback recomendado. No haga cambios durante diagnóstico.

## 5. Copiar páginas de Producción a TEST

1. La solicitud nombra aplicación, páginas y autoriza explícitamente modificar TEST.
2. Valide ambos perfiles; Producción se usa sólo lectura.
3. Explique qué páginas/componentes se copiarán, impacto y riesgo. Recomiende backup, diff y rollback antes de aplicar.
4. Aplique sólo lo autorizado en TEST, valide si corresponde y registre evidencia proporcional. No modifique Producción.

## 6. Copiar TEST a Producción o liberar un cambio

1. Describa con precisión qué objetos, páginas o artefactos se modificarán en Producción, junto con impacto y riesgo.
2. Solicite y registre autorización **explícita, separada y previa** para esa modificación. Una autorización para TEST no es válida para Producción.
3. Valide el perfil autorizado de Producción en lectura antes de iniciar.
4. Recomiende QA TEST, backup, rollback, evidencia y manifiesto según riesgo, alcance y si el flujo fue gestionado por las skills. No los imponga para un cambio menor ya validado por el usuario fuera de las skills.
5. Ejecute exclusivamente la modificación autorizada y registre el resultado. Si falla, aplique el rollback disponible o informe la contingencia acordada.
