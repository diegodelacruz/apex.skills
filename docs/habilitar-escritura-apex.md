# Habilitar escritura APEX

## Acceso Oracle/APEX

No se configura una matriz fija de permisos por ambiente dentro de las skills. Use la credencial configurada para el ambiente pedido; Oracle/APEX decide según los grants vigentes otorgados por el DBA/APEX administrator. Al inicio, verifique cuenta y destino con una ruta de solo lectura cuando esté disponible. Use el MCP Oracle/APEX, SQLcl, App Builder o la ruta configurada adecuada para la operación. La solicitud directa define alcance; no solicite aprobaciones adicionales.

El bootstrap no agrega ni elimina registros MCP. Si el MCP deseado no está
registrado, el usuario puede registrarlo con el wrapper del entorno; la falta
de registro no constituye una prohibición de las skills sobre otros canales.
