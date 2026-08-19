# Uso de APEX Skills desde terminal con Codex CLI

Una skill no es un comando de PowerShell o CMD. Codex CLI es el agente que descubre y aplica las skills; la terminal se usa para instalar las skills, preparar el MCP y abrir Codex dentro del proyecto.

## Instalación única en el equipo

Desde la raíz de `apex.skills`, ejecute en PowerShell:

```powershell
.\scripts\Install-ApexSkillsForCodex.ps1
```

El instalador registra cada skill bajo `%USERPROFILE%\.codex\skills` (o `%CODEX_HOME%\skills` si esa variable está definida) usando un *junction* de Windows. Por ello, después de un `git pull` en este repositorio, las actualizaciones quedan disponibles al iniciar una nueva sesión de Codex CLI.

Si el repositorio y `CODEX_HOME` están en unidades distintas, use una copia:

```powershell
.\scripts\Install-ApexSkillsForCodex.ps1 -Mode Copy
```

En ese modo, vuelva a ejecutar el comando con `-Force` después de cada actualización; el instalador conserva la versión anterior como una carpeta con sufijo `.backup-<fecha-hora>`.

Para CMD:

```cmd
powershell -ExecutionPolicy Bypass -File "<RUTA_APEX_SKILLS>\scripts\Install-ApexSkillsForCodex.ps1"
```

## Usar Codex CLI en un proyecto

Primero prepare el entorno compartido y el MCP una vez, según [Inicialización Codex](inicializacion-automatica-codex.md). Luego abra una terminal en la raíz del proyecto y ejecute:

```powershell
cd "<RUTA_PROYECTO_APEX>"
codex
```

Describa la necesidad normalmente; no escriba `usa apex`:

```text
Revisa la página 120 de la aplicación 109 en TEST y determina por qué está lenta.
```

La forma abreviada `109.201`, cuando acompaña una referencia a página, significa la página 201 de la aplicación 109:

```text
Revisa la página 109.201 en producción, en solo lectura.
```

```text
Analiza el paquete data.pk_ejemplo en producción, en solo lectura, y propone optimizaciones.
```

El coordinador reconoce el contexto Oracle/APEX y selecciona las skills necesarias. Si el pedido menciona TEST o Producción, valida primero el perfil solicitado en modo lectura. Los cambios siguen requiriendo las aprobaciones establecidas.

## Comandos operativos, no skills

Estos comandos preparan herramientas; no sustituyen a Codex CLI ni invocan una skill por sí solos:

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
codex mcp list
```

Use directamente los validadores cuando necesite evidencia reproducible, por ejemplo:

```powershell
python .\skills\oracle-data-change-governance-final\scripts\validate_sql_style.py "<ARCHIVO_O_CARPETA_SQL>"
```

## Otros agentes de terminal

Claude, Cursor, Gemini u otro agente no descubren automáticamente las skills de Codex CLI. Configure su mecanismo propio de skills o indíquele la ruta de `SKILL.md` correspondiente. Las instrucciones y scripts del repositorio son reutilizables, pero el descubrimiento e invocación dependen del agente.
