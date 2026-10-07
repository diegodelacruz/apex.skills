# Credenciales y alineación TEST/Producción

## Credenciales

Todas las herramientas locales de este repositorio leen sus perfiles Oracle y
APEX del archivo `.env` ignorado por Git en la raíz. El proceso no recurre a
variables de proceso ni almacenes del sistema para completar perfiles.
El archivo contiene secretos en texto plano: limita el acceso al archivo y no
lo compartas ni lo agregues al repositorio. Los perfiles anteriores de otros
almacenes pueden permanecer, pero no se consultan.

El perfil elegido para el ambiente solicitado determina la identidad de
conexión. Los privilegios efectivos concedidos por el DBA/APEX administrator
determinan qué operaciones son posibles; no hay usuarios ni grants hardcodeados
en las skills. Al inicio, confirma cuenta y destino reales con una inspección
de solo lectura. Un error de conexión o permiso se reporta desde la herramienta
y no se reemplaza silenciosamente el ambiente solicitado.

## Edición de páginas existentes

La comparación entre ambientes es opcional y no condiciona el cambio solicitado. Informe diferencias observadas cuando ayuden a explicar el resultado.

Al terminar el desarrollo, el SQL exportado de TEST y su manifiesto de instalación se guardan en:

```text
control-proyecto/cambios/<id-cambio>/release/
```

Ese artefacto puede instalarse cuando forma parte del alcance solicitado, mediante una ruta disponible y la cuenta del usuario. La herramienta reporta el resultado y cualquier denegación efectiva.
