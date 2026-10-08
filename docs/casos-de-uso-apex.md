# Casos de uso para agentes Oracle APEX

Use identificadores, rutas y ambientes del proyecto activo; nunca copie nombres, IDs, SQL o datos de un proyecto anterior.

El coordinador se activa por contexto: APEX, Oracle, Application Express/App Express, aplicaciones, páginas, regiones, paquetes, funciones, procedimientos, tablas, vistas, triggers, SQL, PL/SQL, errores ORA y solicitudes de rendimiento. No exija una frase de invocación. Tolere variantes frecuentes de Oracle (`orcle`, `oracel`, `orcale`, `oracl`, `oralce`) y APEX (`apx`, `apxe`, `apexx`, `a-pex`, `apek`) cuando el resto del pedido confirme el contexto. Si no lo confirma, solicite aclaración antes de usar perfiles o herramientas.

## Alcance y acceso

La solicitud directa define acción, alcance y ambiente. Use la credencial configurada para ese ambiente; los permisos efectivos otorgados por el DBA/APEX administrator determinan qué puede ejecutar. Verifique al inicio la sesión y destino reales con herramientas de solo lectura cuando estén disponibles. Perfil/bootstrap y comparación no son gates; no agregue aprobaciones ni pida al usuario ejecutar consultas que el agente puede realizar. Si una ruta falla, pruebe otra configurada para el mismo ambiente.

## 1. Reservar páginas por proyecto

1. Reciba aplicación, proyecto y rango inclusivo.
2. Consulte los ambientes solicitados y compare ocupación/nombres si está disponible.
3. Compare reservas activas de otros proyectos en la carpeta de aplicación.
4. Si existe cruce o diferencia, repórtelo; continúe con el alcance solicitado según permisos efectivos.
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
2. Inspeccione diferencias de ambientes si es útil.
3. Realice el cambio solicitado en el ambiente indicado; informe el resultado real de la herramienta y los controles realizados.

## 5. Diagnosticar un error comparando TEST y Producción

1. Registre síntoma reproducible y valide ambos perfiles en lectura.
2. Confirme identidad exacta en ambos ambientes; compare fuente efectiva, componentes y objetos dependientes.
3. Para SQL/PLSQL, compare firmas, sobrecargas, dependencias, compilación y sinónimos.
4. Registre diferencias, causa, alcance, plan TEST y rollback recomendado. No haga cambios durante diagnóstico.

Si el usuario confirma una corrección propuesta, conserve objeto, impacto,
baseline y validaciones en un paquete de cambio; no repita el inventario
completo antes de aplicar.

## 6. Copiar páginas de Producción a TEST

1. Use aplicación, páginas y ambiente indicados en la solicitud.
2. Valide ambos perfiles y cualquier rango reservado.
3. Explique páginas/componentes, impacto y riesgo; recomiende backup, diff y rollback.
4. Aplique sólo lo autorizado en TEST; no modifique Producción.

## 7. Copiar TEST a Producción o liberar un cambio

1. Ejecute el cambio de Producción indicado en la solicitud por la ruta disponible.
2. Informe impacto, riesgo, resultado y contingencia; Oracle/APEX reportará cualquier falta de privilegio.
