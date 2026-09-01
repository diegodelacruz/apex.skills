# Habilitar operaciones de escritura APEX desde Codex

## Diagnóstico del flujo actual

El comando habitual:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\Users\ddelacruz\Desktop\Python\codex\apex.zml"
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.zml"
codex
```

prepara únicamente el perfil `test` y registra `apex-mcp-test`. El inicializador no registra Producción ni cambia permisos Oracle. Por eso una tarea que intenta crear, modificar o copiar páginas en Producción puede quedar limitada a lectura.

También existe una segunda limitación: el repositorio tiene como objetivo APEX 24.1.3 y mantiene el upstream `apex-mcp` 24.2 en inspección/dry-run hasta que su compatibilidad mutante sea aprobada y validada en TEST. Cambiar el usuario o registrar el servidor no elimina esta incompatibilidad.

## Requisitos para permitir escritura

Deben cumplirse todos estos requisitos:

1. El perfil seguro del ambiente debe existir y validar correctamente.
2. El usuario Oracle debe tener los grants necesarios para las APIs de APEX y el esquema objetivo.
3. El servidor `apex-mcp` debe ser compatible con la versión de APEX instalada.
4. Codex debe tener registrado el servidor MCP del ambiente correcto.
5. La tarea debe declarar explícitamente el alcance de la escritura.

El archivo `.env.example` no concede permisos. `READ_ONLY_USER` es solo un ejemplo; los permisos efectivos los determina Oracle y el usuario configurado en el keyring.

## Preparar TEST para desarrollo

Mantén el comando habitual y usa un perfil TEST con escritura:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\manage_apex_credentials.py import-env --environment test
.\scripts\manage_apex_credentials.py validate --environment test
python .\scripts\validate_apex_mcp_handshake.py --environment test
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\Users\ddelacruz\Desktop\Python\codex\apex.zml"
```

El usuario del perfil TEST debe tener permisos de escritura solamente sobre la aplicación, workspace y objetos que correspondan al desarrollo.

## Registrar Producción cuando exista autorización

Primero importa y valida el perfil autorizado, sin compartir secretos:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\manage_apex_credentials.py import-env --environment production
.\scripts\manage_apex_credentials.py validate --environment production
python .\scripts\validate_apex_mcp_handshake.py --environment production
```

El inicializador actual no registra Producción automáticamente. Comprueba el estado y registra el servidor solo si todavía no aparece:

```powershell
codex mcp list
codex mcp add apex-mcp-production -- ".\.venv\Scripts\python.exe" ".\scripts\run_apex_mcp_with_profile.py" --environment production
```

Después cierra la tarea actual y abre una tarea nueva en `apex.zml`, porque los servidores MCP `stdio` se inician al crear la tarea o sesión.

## Prompt de escritura recomendado

Para desarrollo:

```text
Trabaja en TEST sobre la aplicación <APP_ID>. Te autorizo a crear y modificar
únicamente la página <PAGE_ID>. Primero inspecciona la aplicación y el esquema,
presenta el plan y usa dry-run. Después ejecuta los cambios aprobados y valida
la página. No uses Producción.
```

Para una operación autorizada en Producción:

```text
Trabaja en Producción sobre la aplicación <APP_ID>. Autorizo explícitamente
operaciones de escritura dentro del alcance siguiente: <ALCANCE>. Puedes crear,
modificar o copiar la página <PAGE_ID>. Conserva evidencia, valida antes y
después, y no cambies componentes fuera del alcance.
```

## Si sigue bloqueado

- Si `codex mcp list` no muestra `apex-mcp-production`, el problema es el registro del MCP.
- Si falla `validate`, el problema es perfil, red, wallet, credenciales o permisos Oracle.
- Si la conexión valida pero el agente rechaza escribir, el bloqueo es la política de compatibilidad/seguridad del repositorio o la instrucción de la tarea.
- Si la herramienta de escritura no aparece, el servidor MCP instalado no expone esa operación o la versión no es compatible.

No basta con cambiar el texto `READ-ONLY` de la documentación. Para retirar permanentemente la protección de Producción habría que cambiar las skills, la política, los adaptadores y sus auditorías; eso sería una modificación del ecosistema, no una configuración de conexión.
