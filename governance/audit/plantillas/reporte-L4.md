# Reporte de Auditoría L4 — Piloto de Uso Real

| Campo | Valor |
|---|---|
| **audit_id** | AUD-AAAA-MMDD-L4-NNN |
| **nivel** | L4 |
| **fecha** | AAAA-MM-DDTHH:MM:SS-05:00 |
| **revision** | (commit SHA completo) |
| **scope** | (escenarios piloto ejecutados) |
| **tester** | (identidad del tester externo) |
| **es_contribuidor** | false |
| **resultado** | PASS / FAIL / PASS_WITH_OBSERVATIONS |

## Declaración de independencia

Declaro que no soy contribuidor de este repositorio y que ejecuté las pruebas
piloto sin asistencia del equipo de desarrollo, usando exclusivamente la
documentación disponible.

## Resumen ejecutivo

(1-3 oraciones: qué escenarios se probaron, resultado general, experiencia
del tester)

## Perfil del tester

- Experiencia con Oracle APEX: (nivel)
- Experiencia con Claude/agentes: (nivel)
- Tiempo dedicado a la prueba: (horas)

## Escenarios ejecutados

### Escenario 1: Bootstrap de proyecto

| Control | Resultado | Observaciones |
|---|---|---|
| L4-01: Bootstrap completa sin errores | PASS/FAIL | |
| Tiempo de bootstrap: | (minutos) | |
| Errores encontrados: | (cantidad) | |

### Escenario 2: Invocación de skills

| Control | Resultado | Observaciones |
|---|---|---|
| L4-02: /apex rutea correctamente | PASS/FAIL | |
| Skills probadas: | (lista) | |
| Invocaciones exitosas: | N/M | |
| Invocaciones fallidas: | (detalle) | |

### Escenario 3: Producción de artefactos

| Control | Resultado | Observaciones |
|---|---|---|
| L4-03: Artefacto válido en TEST | PASS/FAIL | |
| Tipo de artefacto: | (página, región, proceso, etc.) | |
| Entorno: | TEST | |

### Escenario 4: Detección de defectos

| Control | Resultado | Observaciones |
|---|---|---|
| L4-04: QA detecta defecto plantado | PASS/FAIL | |
| Tipo de defecto plantado: | (descripción) | |
| Detectado por skill: | (nombre) | |

### Escenario 5: Autonomía documental

| Control | Resultado | Observaciones |
|---|---|---|
| L4-05: Tarea completada sin asistencia | PASS/FAIL | |
| Documentación consultada: | (lista) | |
| Gaps identificados: | (lista) | |

### Escenario 6: Tiempo de ejecución

| Control | Resultado | Observaciones |
|---|---|---|
| L4-06: Tiempo dentro de rango esperado | PASS/FAIL | |
| Tiempo real: | (minutos) | |
| Tiempo esperado: | (minutos) | |

## Hallazgos

| ID | Severidad | Escenario | Descripción | Estado |
|---|---|---|---|---|
| H-NNN | CRITICO/ALTO/MEDIO/BAJO/INFO | L4-XX | | ABIERTO |

## Experiencia del tester

(Narrativa libre: qué fue fácil, qué fue confuso, qué faltó, qué sobró.
Esta sección es especialmente valiosa para mejorar la documentación y
la experiencia de onboarding.)

## Conclusión

(Resultado final. Recomendaciones para mejorar la experiencia de uso real.)
