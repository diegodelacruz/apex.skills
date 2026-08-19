# Casos de uso para agentes Oracle APEX

Use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

El coordinador se activa por contexto: APEX, Oracle, Application Express/App Express, aplicaciones, páginas, regiones, paquetes, funciones, procedimientos, tablas, vistas, triggers, SQL, PL/SQL, errores ORA y solicitudes de rendimiento. No exija una frase de invocación. Tolere variantes frecuentes de Oracle (`orcle`, `oracel`, `orcale`, `oracl`, `oralce`) y APEX (`apx`, `apxe`, `apexx`, `a-pex`, `apek`) cuando el resto del pedido confirme el contexto. Si no lo confirma, solicite aclaración antes de usar perfiles o herramientas.

## Regla de acceso obligatoria

El primer paso de toda solicitud que mencione TEST, Producción, Oracle, APEX, una aplicación, página u objeto es validar el perfil del ambiente solicitado con una operación de sólo lectura. Si el perfil falta, falla o no autoriza el acceso, el agente registra la limitación y no continúa ese flujo ni sustituye el ambiente sin autorización.

## 1. Reservar páginas por proyecto

1. Reciba aplicación, proyecto y rango inclusivo.
2. Valide ambos perfiles y compare ocupación/nombres del rango en TEST y Producción.
3. Compare reservas activas de otros proyectos en la carpeta de aplicación.
4. Si existe cruce o diferencia, genere `environment-diff.md` y espere decisión explícita antes de crear, editar o reservar.
5. Si no existe conflicto, cree la carpeta del proyecto con `pruebas/` y `produccion/`, actualice el registro y aplique la convención Page Name/Title.

## 2. Inspeccionar una aplicación, página u objeto

1. Identifique ambiente, aplicación/página u objeto y propósito.
2. Valide el perfil solicitado en lectura.
3. Inspeccione metadatos, fuente, dependencias, compilación o definición sin cambios.
4. Entregue evidencia, resultado y limitaciones.

## 3. Diagnosticar lentitud u optimizar código Oracle

1. Identifique el ambiente, objeto o componente, síntoma, caso reproducible y alcance.
2. Valide el perfil solicitado en lectura; si se requiere comparar, valide ambos perfiles.
3. Inspeccione fuente, plan, dependencias, firmas, estadísticas y evidencia disponible sin cambios.
4. Entregue causa, impacto, recomendación y plan; aplique gobierno DATA sólo si el usuario solicita implementar una corrección.

## 4. Modificar una página existente

1. Identifique aplicación, página, componente y comportamiento esperado.
2. Valide perfiles TEST/Producción y el rango de proyecto si aplica.
3. Ejecute `apex-environment-alignment-complete` antes de editar.
4. Cree `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
5. Corrija en TEST y prepare controles proporcionales. Para modificar Producción, solicite aprobación explícita independiente.

## 5. Diagnosticar un error comparando TEST y Producción

1. Registre síntoma reproducible y valide ambos perfiles en lectura.
2. Confirme identidad exacta en ambos ambientes; compare fuente efectiva, componentes y objetos dependientes.
3. Para SQL/PLSQL, compare firmas, sobrecargas, dependencias, compilación y sinónimos.
4. Registre diferencias, causa, alcance, plan TEST y rollback recomendado. No haga cambios durante diagnóstico.

## 6. Copiar páginas de Producción a TEST

1. La solicitud nombra aplicación, páginas y autoriza explícitamente modificar TEST.
2. Valide ambos perfiles y cualquier rango reservado.
3. Explique páginas/componentes, impacto y riesgo; recomiende backup, diff y rollback.
4. Aplique sólo lo autorizado en TEST; no modifique Producción.

## 7. Copiar TEST a Producción o liberar un cambio

1. Describa con precisión objetos, páginas o artefactos, impacto y riesgo.
2. Solicite y registre autorización **explícita, separada y previa** para Producción.
3. Valide el perfil de Producción en lectura antes de iniciar.
4. Recomiende controles proporcionales al riesgo; ejecute exclusivamente lo autorizado y registre resultado/contingencia.
