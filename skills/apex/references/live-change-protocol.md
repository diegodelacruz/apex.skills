# Protocolo de cambios en vivo

Usa este protocolo cuando una conversación pasa de inspección a un cambio
Oracle o APEX. No añade una aprobación artificial: una instrucción explícita
como "cambia esto" autoriza el alcance que el usuario acaba de confirmar.

## Estados

1. **Diagnóstico:** solo lectura. Devuelve causa, alcance, impacto previsto y
   una propuesta concreta.
2. **Propuesta:** explica qué objeto o componente cambiará, la regla funcional,
   dependencias relevantes, validación y rollback. Si falta una decisión de
   negocio material, pregunta solo por esa decisión.
3. **Cambio confirmado:** conserva el contexto vivo: ambiente e identidad
   observados, objetivo, fingerprint base, propuesta aceptada y validaciones.
   No repitas inventarios, memoria ni descubrimiento que ya respondieron el
   caso.
4. **Ejecución:** genera un paquete `change.json` con snapshot, preflight,
   apply, verify y rollback. Usa `execute_change_bundle` o
   `Invoke-OracleApexChange.ps1` cuando el preflight compara la fingerprint y
   emite el marcador `__CHANGE_BASELINE_OK=<fingerprint>`.
5. **Resultado:** informa el resultado Oracle/APEX, la validación funcional
   realizada, tiempos observados y el rollback disponible. El rollback es
   explícito; no se ejecuta automáticamente para DDL.

## Ruta rápida y salida segura

La ruta rápida solo aplica si el preflight confirma que el objeto sigue en el
estado diagnosticado y emite exactamente ese marcador. El ejecutor inspecciona
la salida antes de invocar `apply`; si falta el marcador, devuelve
`BASELINE_MISMATCH` y no aplica el cambio. Si cambia la fingerprint, una dependencia o la regla
funcional, detén el paquete antes de `apply` y vuelve a diagnosticar. Un fallo
de compilación o importación se informa con su error real y el snapshot queda
disponible para la reversión solicitada.

## Paquete mínimo

El archivo `change.json` usa `version: 1`, un `id`, `kind`, `target`,
`baseline.fingerprint` y rutas relativas a `preflight.sql`, `apply.sql`,
`verify.sql` y `rollback.sql`; `snapshot.sql` es opcional pero recomendado para
DDL y obligatorio cuando la reversión dependa de la definición anterior.
