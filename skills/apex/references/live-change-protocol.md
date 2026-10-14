# Protocolo de cambios en vivo

Usa este protocolo para cambios Oracle o APEX. Antes de modificar se requiere
una sola confirmación que identifique ambiente, objeto y acción, y una respuesta
explícita de sí/no a si desea backup. No ejecutes si falta una de las dos
decisiones. Si el usuario omite o deja ambigua la decisión de backup, pregunta
solo eso y espera. La decisión completa es la única confirmación; no solicites
otra aprobación salvo que cambie el alcance.

## Estados

1. **Lectura:** una solicitud de revisar, consultar o mostrar datos/especificaciones
   es read-only. Sigue la regla de lectura inmediata de `skills/apex/SKILL.md`;
   no inicies este protocolo ni una validación de cambios.
2. **Aclaración necesaria:** pregunta solo si no se puede determinar el objetivo,
   ambiente o alcance solicitado. No calcules filas afectadas como paso previo
   estándar para INSERT, UPDATE, DELETE, MERGE u otra transacción.
3. **Confirmación única:** presenta ambiente, objetivo y acción concreta; pide
   respuestas explícitas para confirmar la ejecución y para backup sí/no. Si
   falta cualquiera, pregunta solo la decisión pendiente y no ejecutes todavía.
   Si responde que no quiere backup, no crees tabla de respaldo, snapshot ni
   artefacto temporal cuyo fin sea respaldar el estado anterior. Si responde
   que sí, prepara únicamente el backup pertinente a ese cambio.
4. **Ejecución:** conserva identidad y destino verificados en la sesión. Para una
   transacción DML puntual, usa la ruta directa `execute_sql_file` o SQLcl,
   registra la operación y verifica su resultado sin generar `change.json`,
   preflight de huella, snapshot o rollback de paquete por rutina. Usa el bundle
   para una corrección existente cuyo estado base deba compararse antes de
   aplicar, o para cambios coordinados de varios objetos; incluye snapshot solo
   si el usuario pidió backup. Las herramientas controladas requieren los
   campos `confirmed=true` y `backup_choice=yes/no`. La ruta SQL directa requiere
   un `backup_sql_path` específico cuando la respuesta es sí. El bundle requiere
   `snapshot.sql` y lo ejecuta después del preflight y antes de apply. Si elige
   no, el bundle no puede declarar `snapshot` en `change.json`. Si el backup
   aceptado falta o falla, detén el cambio; no conviertas sí en no.
5. **Resultado:** informa la operación ejecutada y su resultado observado. No
   expliques rollback rutinariamente; hazlo si el usuario lo solicita o si una
   limitación concreta afecta el cambio.

## Ruta rápida y salida segura

Cuando se use un bundle, el preflight debe confirmar la huella diagnosticada y
emitir exactamente el marcador. Si falta, devuelve `BASELINE_MISMATCH` y no
aplica el cambio. Si cambia la huella, una dependencia o la regla funcional,
detén el paquete y vuelve a diagnosticar. Este control no se ejecuta para una
lectura simple ni se añade a una transacción DML puntual sin una necesidad
concreta.

## Paquete mínimo

El archivo `change.json` usa `version: 1`, un `id`, `kind`, `target`,
`baseline.fingerprint` y rutas relativas a `preflight.sql`, `apply.sql` y
`verify.sql`. `rollback.sql` es opcional; si se declara, debe existir dentro del
checkout, pero no se ejecuta automáticamente ni demuestra que la reversión sea
segura. `snapshot.sql` es opcional en el manifiesto, pero obligatorio y ejecutado
antes de apply cuando el usuario acepta backup. Si elige no, no declares
`snapshot` en el manifiesto. El bundle no es el flujo predeterminado para DML puntual.
