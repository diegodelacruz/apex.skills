# Layout and range register

This structure is additional to `control-proyecto/`; never move or replace existing project-control artifacts.

```text
<raiz-proyecto>/
  control-proyecto/
  aplicaciones/
    aplicacion-<numero>/
      registro-rangos-paginas.md
      <nombre-proyecto>/
        proyecto.md
        pruebas/
        produccion/
```

Use a filesystem-safe project folder name. Keep the user-facing project name in `proyecto.md` exactly as decided.

## `proyecto.md` minimum content

```markdown
# Proyecto: <nombre-proyecto>

| Campo | Valor |
| --- | --- |
| Aplicación | <numero> |
| Rango inclusivo | <desde>-<hasta> |
| Estado TEST | pendiente/verificado/bloqueado |
| Estado Producción | pendiente/verificado/bloqueado |
| Convención Page Name | <nombre-proyecto>-<nombre-pagina> |
| Convención Page Title | <nombre-pagina> |

## Decisión de rango

<evidencia de ocupación, diferencias y decisión del usuario>
```

## `registro-rangos-paginas.md` minimum content

```markdown
# Registro de rangos de páginas — Aplicación <numero>

| Proyecto | Desde | Hasta | TEST | Producción | Estado | Evidencia |
| --- | ---: | ---: | --- | --- | --- | --- |
| <nombre-proyecto> | <desde> | <hasta> | verificado | verificado | reservado | <ruta-a-environment-diff.md> |
```

Ranges are inclusive. Check every active/reserved row for overlap using `new_from <= existing_to AND new_to >= existing_from`.
