# Estructura estándar de proyecto APEX

Cada proyecto debe versionar una carpeta visible llamada `control-proyecto/`. Allí viven los artefactos generados o mantenidos por las skills; el código fuente APEX/Oracle conserva su propia estructura.

```text
mi-proyecto-apex/
├─ control-proyecto/
│  ├─ decisiones/
│  │  └─ decisiones-globales.md
│  ├─ planes/
│  │  └─ plan-maestro.md
│  ├─ cambios/
│  │  └─ <id-cambio>/
│  │     ├─ decisions.md
│  │     ├─ implementation-plan.md
│  │     └─ 01_precheck.sql ... 09_rollback.sql
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

- `decisiones-globales.md` registra decisiones transversales del usuario y agentes.
- Cada cambio posee su propio `decisions.md` e `implementation-plan.md`; no mezclar decisiones de cambios distintos.
- El plan maestro enlaza cambios, estados, versiones y manuales.
- Capturas, trazas y reportes QA no se mezclan con el manual final: el manual consume únicamente evidencia QA aprobada.
- `manuales/fuentes/` almacena JSON/Markdown editable y el manifiesto de cobertura; `manuales/img/` guarda capturas aprobadas.
- Versione todos estos archivos. Excluya secretos, sesiones, wallets, `.env`, trazas con datos sensibles y archivos de autenticación Playwright.
