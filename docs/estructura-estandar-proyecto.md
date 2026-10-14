# Estructura estándar de proyecto APEX

Cada proyecto debe versionar una carpeta visible llamada `control-proyecto/`. Allí viven los artefactos generados o mantenidos por las skills; el código fuente APEX/Oracle conserva su propia estructura.

```text
mi-proyecto-apex/
├─ control-proyecto/
│  ├─ decisiones/
│  │  └─ decisiones-globales.md
│  ├─ planes/
│  │  └─ plan-maestro.md
│  ├─ cambios/                          # solo para cambio formal/coordinado
│  │  └─ <id-cambio>/
│  │     ├─ change.json                 # cuando se justifica bundle/preflight
│  │     ├─ preflight.sql
│  │     ├─ apply.sql
│  │     ├─ verify.sql
│  │     ├─ rollback.sql                # opcional; nunca se ejecuta automáticamente
│  │     ├─ snapshot.sql                # solo si el usuario pidió backup
│  │     ├─ decisions.md                # requerido para cambio formal
│  │     └─ implementation-plan.md     # requerido para cambio formal
│  ├─ evidencia/
│  │  └─ <id-cambio>/
│  ├─ qa/
│  │  └─ <id-cambio>/
│  │     ├─ reports/
│  │     ├─ screenshots/
│  │     └─ traces/
│  └─ manuales/
│     ├─ img/
│     ├─ fuentes/
│     └─ manual_usuario_<version>.docx
├─ app/
│  └─ exports/
└─ <fuente-apex-oracle-versionada>/
```

## Reglas

- `decisiones-globales.md` registra decisiones transversales del usuario y agentes cuando el proyecto requiere workspace formal; no es requisito para una petición puntual.
- Una lectura no crea carpeta de cambio ni artefactos: consulta directamente después de verificar el destino si hace falta.
- Una operación puntual de datos, después de la única confirmación, usa la ruta SQL directa y registra inicio/resultado en `control-proyecto/.bitacora.json`; no requiere carpeta de cambio, conteo previo, `change.json`, snapshot ni plan manual. El registro es local, está ignorado por Git y no es inmutable.
- Usa `change.json` con preflight/apply/verify cuando una huella del objeto o la coordinación de varios objetos protege materialmente el cambio. `rollback.sql` es opcional y no se ejecuta automáticamente; `snapshot.sql` es opcional y se crea solo cuando el usuario pidió o aceptó backup.
- Cambios multiobjeto, migraciones o trabajo de impacto material pueden requerir `decisions.md` e `implementation-plan.md`; justifica el nivel de artefactos por el alcance y conserva solo evidencia aplicable. Un DML puntual no requiere entrada al plan maestro ni carpeta.
- El plan maestro enlaza cambios, estados, versiones y manuales.
- Capturas, trazas y reportes QA no se mezclan con el manual final: el manual consume únicamente evidencia QA aprobada.
- `manuales/fuentes/` almacena JSON/Markdown editable y el manifiesto de cobertura; `manuales/img/` guarda capturas aprobadas.
- Versione todos estos archivos. Excluya secretos, sesiones, wallets, `.env`, trazas con datos sensibles y archivos de autenticación Playwright.
