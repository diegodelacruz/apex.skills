# Credenciales y alineación TEST/Producción

## Credenciales

Las credenciales se mantienen fuera del repositorio. Un perfil local es un medio de conexión, no una condición para proceder; use la herramienta disponible con el ambiente y alcance indicados por el usuario.

| Plataforma | Almacén recomendado |
| --- | --- |
| Windows | Credential Manager o SecretManagement |
| macOS | Keychain |
| Linux | Secret Service |

El perfil/credencial configurado para el ambiente solicitado determina la identidad de conexión. Los privilegios efectivos concedidos por el DBA/APEX administrator determinan qué operaciones son posibles; no hay usuarios ni grants hardcodeados en las skills. Al inicio, use inspección de solo lectura para confirmar cuenta y destino reales y, cuando esté disponible, privilegios de sesión. Un error de conexión o permiso se reporta desde la herramienta y no se reemplaza silenciosamente el ambiente solicitado. El sondeo de grants es informativo, no sustituye la autorización efectiva que Oracle/APEX comprueba al ejecutar.

## Edición de páginas existentes

La comparación entre ambientes es opcional y no condiciona el cambio solicitado. Informe diferencias observadas cuando ayuden a explicar el resultado.

Al terminar el desarrollo, el SQL exportado de TEST y su manifiesto de instalación se guardan en:

```text
control-proyecto/cambios/<id-cambio>/release/
```

Ese artefacto puede instalarse cuando forma parte del alcance solicitado, mediante una ruta disponible y la cuenta del usuario. La herramienta reporta el resultado y cualquier denegación efectiva.
