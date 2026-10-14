# Hook local de registro

`.hooks/pre-commit.sh` añade metadatos de los archivos staged a
`control-proyecto/.bitacora.json` como una línea JSON. No forma parte de
`.pre-commit-config.yaml`; por eso `pre-commit install` no lo instala ni lo
ejecuta. Se puede invocar manualmente:

```bash
bash .hooks/pre-commit.sh
```

El evento contiene timestamp UTC, rama, autor, correo y nombres de archivos
staged. El hook no registra el contenido de los archivos. Necesita Bash, Python
3 y Git.

La bitácora es un archivo JSON Lines local ignorado por Git. El hook y los
adaptadores controlados anexan eventos, pero un usuario o proceso puede editar
o borrar el archivo; no es un registro inmutable ni a prueba de manipulación.
El hook no reemplaza ni reescribe las líneas existentes.

Para leer los eventos, usa `apex-audit-decisions-log`. Git conserva por separado
el historial de los cambios que sí se hayan confirmado.
