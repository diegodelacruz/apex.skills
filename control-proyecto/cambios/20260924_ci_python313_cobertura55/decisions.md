# CI local, Python base y cobertura

## Objetivo y necesidad

Hacer que una sola orden local ejecute los mismos controles que GitHub Actions,
eliminar fallos actuales de formato/lint/tipos, declarar una versión base única
de Python y alinear el umbral de cobertura que hoy difiere entre configuraciones.

## Decisiones y alcance

- Adoptar Python 3.13 como versión menor base, usando actualizaciones de parche. Coincide con el `.venv` que ya ejecuta la suite completa y con una versión que sigue en soporte oficial.
- Añadir `scripts/run_ci_checks.py` como runner común para Windows local y GitHub Actions.
- Fijar un piso inicial de cobertura de 55%, basado en la medición observada de 57.07% antes de agregar el runner; conservar 80% como meta gradual, no como puerta actual. Tras incluir el runner, la cobertura medida fue 56.16%.
- Actualizar Black a 24.10.0 para que soporte `py313` y mantener alineada la versión del hook pre-commit.
- Corregir los problemas de Black, flake8 y mypy detectados en el módulo de contexto externo.
- Añadir estos cambios a `CHANGELOG.md` bajo `Unreleased` y formalizar en la política la actualización obligatoria del changelog y la auditoría integral antes de cada subida a GitHub.
- Quitar exclusiones globales del detector de secretos de CI, pre-commit y la auditoría de seguridad; extender el control de whitespace a archivos staged y nuevos; refrescar afirmaciones obsoletas de CI y pruebas en la arquitectura.
- Registrar en el baseline los 12 hashes públicos verificados de upstream y probar los controles de whitespace para archivos nuevos y staged.
- Alinear Q05 del auditor de calidad con la invocación Git resuelta y los chequeos de whitespace staged/no-staged.

## Alternativas e impacto

Se consideró subir inmediatamente el umbral a 80%, pero la suite actual no lo alcanza; hacerlo bloquearía CI sin elevar primero la cobertura real. Mantener sólo 20% permitiría regresiones importantes. El piso de 55% preserva la medición actual y deja una ruta gradual hacia 80%.

Python 3.14 es una rama más reciente, pero 3.13 ya es la versión probada en el `.venv` del proyecto. El cambio a 3.13 consolida la matriz previa 3.9/3.10/3.11 y el objetivo obsoleto de Black. No agrega permisos Oracle ni cambia comportamiento de producción. `run_ci_checks.py` ejecuta comandos locales determinísticos y necesita dependencias del `requirements.txt` y Git disponible.

## Validación, rollback y estado

El runner local se ejecutó con Python 3.13.12: 485 pruebas aprobadas, 60.65% de cobertura de líneas, 43.12% de ramas y 56.63% combinada; `pip check`, audit_skill_ecosystem, audit_quality_score, pytest, Black, isort, flake8, mypy, Bandit, detect-secrets y los chequeos de whitespace para cambios staged, unstaged y archivos nuevos pasaron. El hook `pre-commit run detect-secrets --all-files` pasó. `scripts/security-audit.sh` pasó 8/8 controles; avisó que hay 39 paquetes con versiones más recientes disponibles, sin reportar una vulnerabilidad concreta. La cobertura supera el piso vigente de 55%. La suite conserva 10 `DeprecationWarning` por `datetime.utcnow()` en el módulo de contexto externo; no causan fallos. La revisión independiente confirmó que no quedan bloqueantes técnicos o de seguridad y verificó la ruta resuelta de Git para los tres comandos del runner.

El changelog registra el runner CI compartido, Python 3.13, el umbral de cobertura, la corrección de formato/lint/tipos, el endurecimiento del escaneo de secretos y las nuevas reglas de cambio/publicación bajo `Unreleased`; no se asigna una versión de release. La revisión independiente del diff completo detectó exclusiones demasiado amplias en CI, pre-commit y la auditoría de seguridad, además de datos documentales obsoletos; se corrigieron y revisaron de nuevo. Se eliminaron las exclusiones globales y de `upstreams.lock.json`, se incluyó `.mcp.json.example` y `tests/fixtures` en el hook, y se añadieron al baseline sólo 12 hashes públicos verificados de commits, archives y overlays. Se actualizaron arquitectura, seguridad, setup de GitHub y las métricas (485 pruebas, 60.65% líneas, 43.12% ramas, 56.63% combinado). El changelog indica v1.2.0, pero no existen tags Git locales ni remotos, así que aún no hay release tag de GitHub. Se añadieron pruebas para whitespace staged/nuevo, se corrigieron el filtro del baseline temporal, el uso de Git por ruta resuelta y Q05. El auditor independiente concluyó que no quedan bloqueantes técnicos o de seguridad. El runner completo, los hooks pre-commit y la auditoría de seguridad pasaron tras las correcciones finales.

Las dependencias continúan declaradas mediante rangos en `requirements.txt`; no se creó un lockfile en este cambio, por lo que una instalación futura puede resolver versiones distintas. Si se requiere reproducibilidad exacta entre instalaciones, crear y validar un lockfile como cambio separado. Si el runner falla, revertir sus cambios de configuración y restaurar los valores previos de Python/cobertura; no revertir cambios preexistentes de otras tareas.

Responsable: Codex. No se accede a Oracle ni se ejecuta SQL.
