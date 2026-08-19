# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3 y objetos Oracle relacionados.

Empiece por [MANUAL-DE-USO.md](MANUAL-DE-USO.md). Describa el objetivo en lenguaje natural: el coordinador detecta el contexto Oracle/APEX y elige las skills especializadas necesarias; no debe escribir `usa apex`.

Para Codex CLI consulte [uso de skills desde terminal](docs/uso-skills-codex-cli.md): las skills se instalan una vez en el directorio de usuario de Codex y luego se usa `codex` desde la carpeta del proyecto.

## Preparación inicial

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
.\scripts\Install-ApexSkillsForCodex.ps1
```

## Principios

- Perfiles TEST/Producción seguros por usuario; sin secretos en Git o documentación.
- Validación de acceso en lectura antes de operar un ambiente.
- Alineación TEST/Producción para páginas existentes y control de rangos por proyecto.
- Cambios a Producción sólo con aprobación explícita separada.
- Gobierno DATA, decisiones, planes, validación SQL y auditoría antes del cierre.

Consulte [dependencias](docs/dependencias.md), [casos de uso](docs/casos-de-uso-apex.md) y [auditoría obligatoria](docs/auditoria-obligatoria.md).
