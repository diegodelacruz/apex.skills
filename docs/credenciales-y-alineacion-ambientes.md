# Credenciales y alineación TEST/Producción

## Credenciales

Las skills requieren perfiles separados para TEST y Producción, pero no guardan secretos dentro del repositorio. Cada usuario registra sus credenciales en su almacén seguro local y el proyecto conserva únicamente el nombre del perfil y estado de acceso.

| Plataforma | Almacén recomendado |
| --- | --- |
| Windows | Credential Manager o SecretManagement |
| macOS | Keychain |
| Linux | Secret Service |

Al iniciar un proyecto se realiza una validación de solo lectura. Si un usuario no tiene acceso a Producción, su estado queda registrado y el flujo continúa en TEST; un operador autorizado instala el release.

## Edición de páginas existentes

Antes de modificar una página se compara obligatoriamente el export/estructura de TEST con Producción. Si hay diferencias, la skill recomienda sincronizar Producción hacia TEST y espera autorización antes de hacerlo. Si se rechaza, documenta el baseline y el riesgo.

Al terminar el desarrollo, el SQL exportado de TEST y su manifiesto de instalación se guardan en:

```text
control-proyecto/cambios/<id-cambio>/release/
```

Ese artefacto está preparado para instalación controlada en Producción, pero no se instala sin autorización explícita y perfil/operador autorizado.
