# APEX Skills

Framework canónico para agentes que desarrollan, validan, liberan y documentan Oracle APEX 24.1.3.

Empiece por [MANUAL-DE-USO.md](MANUAL-DE-USO.md). Para uso normal, invoque la skill corta `apex` o describa la solicitud en lenguaje natural; el coordinador elige las skills especializadas necesarias.

## Preparación inicial

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

## Principios

- Perfiles TEST/Producción seguros por usuario; sin secretos en Git o documentación.
- Validación de acceso en lectura antes de operar un ambiente.
- Alineación TEST/Producción para páginas existentes y control de rangos por proyecto.
- Cambios a Producción sólo con aprobación explícita separada.
- Gobierno DATA, decisiones, planes y auditoría antes del cierre.

Consulte [dependencias](docs/dependencias.md), [casos de uso](docs/casos-de-uso-apex.md) y [auditoría obligatoria](docs/auditoria-obligatoria.md).
