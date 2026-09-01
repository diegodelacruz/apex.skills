# Auditoría integral del repositorio — 2026-09-01

## Alcance

Se revisaron estructura, skills, routing y catálogos, enlaces Markdown,
configuración JSON, dependencias declaradas, scripts, pruebas, estilo, tipos,
seguridad, secretos, PowerShell y el parche de compatibilidad MCP/APEX 24.1.3.
Los upstreams administrados se trataron como artefactos generados y no se
editaron directamente.

## Correcciones aplicadas

- Se corrigió `scripts/validate-config.py` para no depender de emojis que fallan
  con la consola Windows `cp1252`.
- Se normalizó el formato/importación de los scripts del adaptador APEX 24.1.3.
- Se alineó `pyproject.toml` con el umbral efectivo de cobertura de `pytest.ini`.
- Se actualizó `docs/TESTING.md` con el procedimiento Windows y la fecha de
  auditoría.
- Se mantuvo el parche APEX 24.1.3 como cambio canónico y reproducible del
  inicializador.

## Evidencia ejecutada

| Control | Resultado |
|---|---|
| `python scripts/audit_skill_ecosystem.py` | `AUDIT_PASS` |
| `python scripts/audit_quality_score.py` | `QUALITY_AUDIT_PASS: 100/100` |
| `python scripts/validate-config.py` | PASS |
| `python -m pytest tests -v` | 122 passed; 26.34% cobertura |
| `isort --check-only scripts tests` | PASS |
| `flake8 --jobs=1 scripts tests --max-line-length=120` | PASS |
| `mypy --ignore-missing-imports scripts tests` | PASS |
| `bandit -c .bandit.yaml -r scripts tests` | PASS; sin hallazgos |
| `detect-secrets` con exclusión de artefactos generados | PASS |
| Parseo de `Initialize-ApexCodexProject.ps1` | PASS |
| `git diff --check` | PASS |
| Validador APEX 24.1.3 | `APEX_MCP_APEX241_COMPATIBILITY_STATIC_PASS` |

## Limitaciones que no se ocultan

- `black --check scripts tests` inicialmente quedó bloqueado por procesos
  auxiliares de Windows; ejecutado fuera del sandbox pasó correctamente.
- `security-audit.sh` no pudo ejecutarse mediante Git Bash por `Win32 error 5`.
  Sus controles equivalentes (`bandit`, `mypy`, `detect-secrets` y revisión de
  patrones) sí se ejecutaron individualmente.
- La auditoría es determinística y local. La política del repositorio exige una
  revisión independiente antes de publicar cambios.
- La compatibilidad del adaptador no concede privilegios Oracle ni demuestra
  una escritura real en Producción; eso requiere validación controlada y los
  grants DBA correspondientes.

## Veredicto

`AUDIT_PASS_WITH_LIMITATIONS`: no quedan fallos reproducibles en los controles
locales ejecutados. Quedan como pasos de publicación la revisión independiente
y la validación funcional autorizada contra TEST/Producción.
