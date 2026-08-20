# Reglas de Formateo Canónicas

**Versión**: 1.0  
**Estado**: Canónico - Aplica a todos los lenguajes y archivos del proyecto  
**Última actualización**: 2026-08-20

Estas 116 reglas definen el estándar de formateo para SQL, PL/SQL, Python, PowerShell y otros lenguajes aplicables en apex.skills. Son **no negociables** y prevalecen sobre configuraciones automáticas (Black, isort, formatters, etc.).

---

## INDENTACIÓN (Aplica a TODOS los lenguajes)

1. Convertir todo el código a minúsculas, excepto el contenido dentro de comillas simples (`'...'`) o dobles (`"..."`).

2. Preservar literalmente el contenido de los literales:
   - Mayúsculas y minúsculas.
   - Acentos.
   - Espacios.
   - Símbolos.
   - Contenido textual.
   - No recortar ni modificar su contenido.

3. **Usar exclusivamente tabuladores reales (`\t`) para la sangría.**

4. **No usar espacios para indentar.**

5. **Asumir un ancho visual de 4 espacios por tabulador.**

---

## CONSULTAS SQL (SELECT)

6. En `select`, colocar cada columna o expresión en su propia línea.

7. Usar coma líder en listas de columnas:
   - La primera expresión no lleva coma.
   - Las siguientes comienzan con `, `.

8. Colocar en una nueva línea las cláusulas principales:
   - `with`
   - `select`
   - `from`
   - `join`
   - `on`
   - `where`
   - `group by`
   - `having`
   - `window`
   - `qualify`
   - `order by`
   - `limit`

9. Aplicar sangría jerárquica a CTE y subconsultas.

10. En CTE, colocar `as (` junto al nombre del CTE.

11. Indentar el cuerpo de cada CTE un nivel adicional.

12. Alinear el paréntesis de cierre `)` del CTE con el nivel del nombre del CTE.

13. Cuando existan varios CTE, utilizar coma líder para separar los CTE posteriores al primero.

14. Formatear las subconsultas aplicando las mismas reglas que a una consulta principal.

15. Alinear el cierre de una subconsulta con el nivel lógico que abrió el paréntesis.

16. Colocar cada `join` en una línea independiente.

17. Aplicar la regla anterior a cualquier tipo de join:
   - `inner join`
   - `left join`
   - `right join`
   - `full join`
   - `cross join`
   - Otros tipos de `join`.

18. Colocar `on` en la línea siguiente al `join`.

19. Indentar `on` respecto al `join`.

20. Separar las condiciones compuestas de un `on`:
   - Una condición por línea.
   - Cada `and` u `or` posterior inicia una nueva línea.

21. Separar las condiciones compuestas de `where` cuando mejore la legibilidad.

22. Colocar cada `and` u `or` de condiciones complejas en una nueva línea.

23. Indentar correctamente los grupos de condiciones encerrados entre paréntesis.

---

## CASE Y OPERADORES

24. Formatear los `case` complejos en múltiples líneas.

25. Separar visualmente:
   - `case`
   - `when`
   - `then`
   - `else`
   - `end`

26. Aplicar sangría jerárquica dentro de un `case`.

27. Permitir un `case` compacto únicamente cuando sea realmente simple y la legibilidad sea mejor.

28. Añadir un espacio después de las comas cuando corresponda.

29. Añadir espacios alrededor de operadores, incluyendo:
   - `=`
   - `<>`
   - `!=`
   - `>=`
   - `<=`
   - `>`
   - `<`
   - `||`
   - `+`
   - `-`
   - `*`
   - `/`
   - `:=`

30. No modificar espacios ni operadores dentro de literales de texto.

31. Añadir espacios alrededor del operador de concatenación `||`.

---

## FUNCIONES Y REFERENCIAS

32. No modificar paréntesis cuando eso pueda alterar la semántica.

33. Organizar los paréntesis según la jerarquía lógica de la expresión.

34. No cambiar nombres de funciones SQL.

35. Mantener intactos los argumentos y su orden.

36. Formatear llamadas a funciones únicamente mediante espacios, saltos de línea y sangría.

37. No inventar, cambiar ni eliminar aliases.

38. No agregar `as` automáticamente a aliases si no existía originalmente.

39. No cambiar nombres de:
   - Tablas.
   - Columnas.
   - Esquemas.
   - Aliases.
   - Paquetes.
   - Procedimientos.
   - Funciones.
   - Triggers.
   - Variables.
   - DB links.
   - Otros objetos.

40. Convertir los nombres anteriores a minúsculas únicamente cuando estén fuera de comillas.

---

## COMENTARIOS

41. Mantener los comentarios `--` sin reescribir su contenido.

42. Mantener los comentarios `/* ... */` sin reescribir su contenido.

43. No corregir ortografía, mayúsculas, acentos ni texto dentro de comentarios.

44. Intentar mantener los comentarios encima de la línea o bloque que documentan.

45. Permitir ajustar la posición de un comentario únicamente para conservar la jerarquía visual, sin modificar su contenido.

---

## DDL (CREATE, ALTER, DROP)

46. Formatear DDL con encabezados separados en líneas lógicas.

47. Aplicar formato a estructuras como:
   - `create table`
   - `create view`
   - `create force view`
   - `create or replace view`
   - `create trigger`
   - `create or replace trigger`
   - `create procedure`
   - `create function`
   - `create package`
   - `create package body`

48. En definiciones de tablas, colocar cada columna en su propia línea.

49. Utilizar coma líder en definiciones de columnas cuando corresponda.

50. Mantener intactos:
   - Tipos de datos.
   - Tamaños.
   - Restricciones.
   - Valores por defecto.
   - Comentarios asociados.

---

## TRIGGERS

51. En triggers, separar en líneas lógicas:
   - Encabezado `create or replace trigger`.
   - Evento.
   - `on`.
   - `for each row`.
   - Cuerpo `begin ... end;`.

52. Aplicar sangría consistente al cuerpo de triggers.

---

## PROCEDIMIENTOS Y FUNCIONES PL/SQL

53. En procedimientos y funciones PL/SQL, dividir la declaración en líneas lógicas.

54. Colocar los parámetros de procedimientos y funciones dentro de un bloque indentado.

55. Utilizar coma líder para parámetros posteriores al primero.

56. Mantener el modo de los parámetros:
   - `in`
   - `out`
   - `in out`

57. No modificar los tipos de datos de parámetros.

58. Formatear bloques `begin ... end` con sangría jerárquica.

59. Indentar todas las instrucciones internas de un `begin` un nivel adicional.

60. Alinear `end` con el `begin` correspondiente.

61. Aplicar sangría adicional a bloques `begin ... end` anidados.

---

## CONDICIONALES Y LOOPS

62. Formatear `if / elsif / else / end if` jerárquicamente.

63. Indentar el contenido de cada rama de un `if`.

64. Formatear loops con jerarquía consistente.

65. Aplicar la misma regla de sangría a:
   - `for ... loop`
   - `while ... loop`
   - `loop ... end loop`

66. Colocar `exception` como sección propia del bloque PL/SQL.

67. Indentar los manejadores `when` dentro de `exception`.

68. Indentar las instrucciones de cada manejador un nivel adicional.

---

## ASIGNACIÓN Y LLAMADAS

69. Normalizar espacios alrededor del operador de asignación `:=`.

70. Formatear llamadas a procedimientos con múltiples parámetros en varias líneas cuando mejore la legibilidad.

71. Mantener las asociaciones de parámetros nombrados mediante `=>`.

72. Usar coma líder en llamadas multilínea a procedimientos cuando corresponda.

---

## INSERT, UPDATE, DELETE

73. En `insert`, separar la lista de columnas cuando la sentencia sea extensa.

74. Colocar una columna por línea en listas de `insert` cuando se expanda.

75. Utilizar coma líder en columnas posteriores a la primera.

76. Separar la cláusula `values` de la lista de columnas.

77. Colocar un valor por línea en listas extensas de `values`.

78. Mantener exactamente el mismo orden entre columnas y valores.

79. En `update`, colocar cada asignación en su propia línea cuando existan varias.

80. Utilizar coma líder para las asignaciones posteriores a la primera.

81. Colocar `where` en una línea independiente en sentencias `update`.

82. En `delete`, colocar `where` en una línea independiente cuando mejore la legibilidad.

---

## SELECT ... INTO (PL/SQL)

83. En PL/SQL, separar lógicamente:
   - `select`
   - `into`
   - `from`
   - `where`

84. En `select ... into`, colocar cada elemento de `select` en su propia línea cuando existan varios.

85. En `into`, colocar cada variable de destino en su propia línea cuando existan varias.

86. Utilizar coma líder en elementos posteriores al primero tanto en `select` como en `into`.

---

## RESTRICCIONES SEMÁNTICAS (Nunca modificar)

87. No cambiar la semántica del código.

88. No corregir automáticamente errores funcionales o lógicos.

89. No agregar condiciones SQL.

90. No eliminar condiciones SQL.

91. No modificar tipos de `join`.

92. No agregar ni eliminar joins.

93. No cambiar relaciones entre tablas.

94. No cambiar valores.

95. No renombrar variables.

96. No cambiar el orden lógico del código salvo cuando el movimiento sea estrictamente de formato y no altere la semántica.

---

## SUGERENCIAS Y ADVERTENCIAS

97. Cuando se detecte una posible inconsistencia, no corregirla automáticamente.

98. Añadir una sugerencia como comentario cuando exista un posible problema.

99. Todas las sugerencias deben comenzar exactamente con: `-- sugerencia:`

100. Las sugerencias deben ser no intrusivas y no afectar la ejecución del código.

101. Intentar colocar las sugerencias junto al bloque relacionado.

102. Cuando sea posible, colocar las sugerencias dentro del contexto del `select` correspondiente.

103. Señalar mediante sugerencias posibles condiciones tautológicas.

104. Señalar mediante sugerencias joins potencialmente incompletos.

105. Señalar mediante sugerencias condiciones que aparentemente siempre producen el mismo resultado.

106. Señalar mediante sugerencias posibles inconsistencias por mezcla de objetos con esquema calificado y sin esquema.

107. Señalar mediante sugerencias aliases potencialmente ambiguos.

108. Señalar mediante sugerencias relaciones que podrían producir duplicados inesperados.

109. Señalar mediante sugerencias condiciones aparentemente redundantes.

110. No aplicar ninguna corrección semántica derivada de una sugerencia salvo que se solicite expresamente.

---

## PRIORIDADES Y APLICACIÓN GENERAL

111. Ante ambigüedad de formato, priorizar en este orden:
    1. Consistencia.
    2. Jerarquía.
    3. Legibilidad.
    4. Mínima alteración del código original.

112. **Por defecto, al recibir SQL o PL/SQL para formatear, devolver únicamente el código formateado.**

113. No agregar introducciones ni explicaciones al código formateado salvo que se soliciten.

114. Incluir únicamente comentarios `-- sugerencia:` adicionales cuando se detecte algo que amerite revisión.

115. Permitir incorporar nuevas reglas de formato indicadas posteriormente por el usuario.

116. Cuando una nueva regla contradiga una anterior, aplicar la regla más reciente indicada por el usuario.

---

## INTEGRACIÓN CON HERRAMIENTAS DE AUTOMATIZACIÓN

**Importante**: Estas reglas prevalecen sobre cualquier configuración de formatters automáticos:
- ❌ Black formatter (convierte TABS → ESPACIOS, viola Reglas 3-5)
- ✅ isort (respetar manualmente, sin Black)
- ✅ flake8 (configurar para permitir TABS)
- ✅ Custom validators (crear si es necesario)

**Pre-commit hooks**: Deben validar conformidad, no formatear automáticamente.

---

## APLICACIÓN POR LENGUAJE

| Lenguaje | Reglas Aplicables | Notas |
|----------|-------------------|-------|
| SQL | 1-110 | Todas aplican completo |
| PL/SQL | 1-110 | Todas aplican completo |
| Python | 1-5, 28-29, 41-45 | Indentación + comentarios |
| PowerShell | 1-5, 28-29, 41-45 | Indentación + comentarios |
| Markdown | 1-5 (parcial) | Código dentro de bloques |
| YAML/JSON | 1-5 (parcial) | Respetando sintaxis |

---

**Última verificación**: Cada skill debe incluir referencia a este documento en su `SKILL.md` bajo "Estándares de código".
