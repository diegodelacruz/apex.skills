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
│  │     ├─ change.json                 # cambio diagnosticado y acotado
│  │     ├─ snapshot.sql
│  │     ├─ preflight.sql
│  │     ├─ apply.sql
│  │     ├─ verify.sql
│  │     ├─ rollback.sql
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

- `decisiones-globales.md` registra decisiones transversales del usuario y agentes.
- Cada cambio posee su propia evidencia y rollback; no mezclar cambios distintos. Un cambio diagnosticado, de objeto o componente acotado puede usar `change.json` con sus seis artefactos. Los cambios multiobjeto, migraciones, destructivos o con reglas de negocio abiertas también requieren `decisions.md` e `implementation-plan.md`.
- El plan maestro enlaza cambios, estados, versiones y manuales.
- Capturas, trazas y reportes QA no se mezclan con el manual final: el manual consume únicamente evidencia QA aprobada.
- `manuales/fuentes/` almacena JSON/Markdown editable y el manifiesto de cobertura; `manuales/img/` guarda capturas aprobadas.
- Versione todos estos archivos. Excluya secretos, sesiones, wallets, `.env`, trazas con datos sensibles y archivos de autenticación Playwright.
