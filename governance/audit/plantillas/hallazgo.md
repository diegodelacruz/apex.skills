# Ficha de Hallazgo

| Campo | Valor |
|---|---|
| **hallazgo_id** | H-NNN |
| **audit_id** | AUD-AAAA-MMDD-LN-NNN |
| **nivel** | L1 / L2 / L3 / L4 |
| **fecha_deteccion** | AAAA-MM-DDTHH:MM:SS-05:00 |
| **control** | (ID del control que lo detectó) |
| **severidad** | CRITICO / ALTO / MEDIO / BAJO / INFO |

## Descripción

(Qué se encontró, en qué archivo, en qué línea. Debe ser reproducible.)

## Archivo(s) afectado(s)

- `ruta/al/archivo.ext` (línea N)

## Impacto

(Qué pasa si no se corrige. Quién se ve afectado.)

## Reproducción

```bash
# Comando o pasos para reproducir el hallazgo
```

## Corrección propuesta

(Qué se debe hacer para resolver. Si hay varias opciones, listarlas.)

## Ciclo de vida

| Estado | Fecha | Responsable | Observaciones |
|---|---|---|---|
| ABIERTO | AAAA-MM-DD | (auditor) | Detección inicial |
| ASIGNADO | | (responsable) | |
| RESUELTO | | (desarrollador) | (commit SHA del fix) |
| VERIFICADO | | (auditor) | (commit SHA verificado) |

## Verificación

- [ ] El fix fue aplicado en un commit posterior
- [ ] El hallazgo ya no se reproduce con el fix aplicado
- [ ] El auditor (o un auditor independiente) verificó la resolución
- [ ] El registro central fue actualizado

## Notas

(Contexto adicional, referencias, decisiones relacionadas.)
