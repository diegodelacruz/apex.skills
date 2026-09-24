# Política central de cierre del ecosistema APEX Skills

Esta matriz se complementa con la [Matriz de calidad interagentes](MATRIZ-CALIDAD-INTERAGENTES.md), que define una calificación reproducible de 100 puntos y gates bloqueantes.

Esta matriz forma parte de la [Política canónica de evolución del ecosistema](POLITICA-EVOLUCION-ECOSISTEMA.md). La política canónica tiene precedencia para controlar la evolución; este documento conserva la matriz técnica de cierre.

Esta política es el criterio obligatorio para cerrar cualquier actualización de
`apex.skills`, aunque el cambio sólo afecte a documentación. Aplica a skills,
catálogos, routing, referencias, scripts, assets, plantillas, configuración,
seguridad, pruebas y documentación Oracle/APEX.

Una actualización no está terminada hasta revisar el repositorio completo, no
sólo los archivos modificados. El inventario real de skills es la fuente de
verdad operativa; actualmente contiene **31 skills** (25 técnicas + 6 orquestadores).

Para crear una skill nueva desde el inicio, aplica la [guía canónica de
creación](GUIA-CREAR-NUEVA-SKILL.md). Esta guía operacionaliza el contrato
portable, la decisión de separación, la integración en routing y catálogos, y
los gates de validación y revisión independiente definidos aquí.

## Compatibilidad con Agent Skills

Cada skill portable debe ser un directorio que contenga un `SKILL.md` en su
raíz. La estructura mínima portable es:

```text
skills/<nombre-de-skill>/
└── SKILL.md
```

El `SKILL.md` debe comenzar con frontmatter YAML válido que incluya, como
mínimo:

```yaml
---
name: nombre-de-skill
description: Descripción clara, breve y orientada al descubrimiento.
---
```

Las reglas portables son:

- `name` es único, coincide exactamente con el directorio y usa minúsculas,
  kebab-case y nombres estables; no contiene espacios, emojis ni aliases
  ambiguos.
- `description` explica qué resuelve la skill, para qué intención debe ser
  descubierta y cuál es su alcance; debe usar términos que un usuario podría
  emplear al solicitar la capacidad, sin depender de conocer el nombre de la
  skill.
- El cuerpo de `SKILL.md` contiene las instrucciones esenciales y se lee de
  forma progresiva: primero `SKILL.md`, después sólo las `references/`,
  `scripts/`, `assets/` o plantillas necesarias para la tarea.
- Los enlaces y rutas dentro de esos recursos deben ser locales, válidos y
  relativos al recurso que los declara cuando sea portable.

El repositorio puede añadir extensiones propias para organización y
descubrimiento local: `category`, `order`, `tags` y
`agents/openai.yaml`. Estas extensiones no sustituyen `name` ni
`description`, no forman parte del mínimo portable y no deben presentarse
como requisitos universales de Agent Skills. En este repositorio,
`category`, `order` y `tags` se validan por unicidad/coherencia;
`agents/openai.yaml` sólo se exige cuando la skill se expone mediante ese
agente.

## Flujo obligatorio de actualización

1. Registre objetivo, alcance, riesgo, responsable, fecha, decisiones,
   limitaciones y evidencia en el plan/espacio de proyecto correspondiente.
2. Revise estado Git, rama, cambios remotos, inventario real de
   `skills/*/SKILL.md` y documentos que declaran el número de skills.
3. Mantenga el routing mínimo y canónico en
   `skills/apex/references/routing.md`; no duplique autoridad ni relaje
   aprobaciones de las skills existentes.
4. Sincronice todos los catálogos y documentos declarativos, incluidos
   `skills/README.md`, `skills/SKILLS-QUICK-REFERENCE.md`, `README.md`,
   `CLAUDE.md`, `docs/ARCHITECTURE.md` y cualquier índice equivalente.
5. Actualice `CHANGELOG.md`, decisiones y planes cuando el cambio afecte
   capacidades, gobernanza o criterios de cierre.
6. Ejecute la matriz siguiente sobre el repositorio completo. Cada control se
   marca `PASS`, `FAIL` o `N/A`. Todo `N/A` debe incluir una justificación
   concreta; un `FAIL` bloquea el cierre.

## Matriz de consistencia integral

| ID | Control de cierre | Resultado (`PASS`/`FAIL`/`N/A`) | Evidencia o justificación |
| --- | --- | --- | --- |
| C01 | Todos los directorios de skill esperados existen y contienen un `SKILL.md` legible, con frontmatter válido. |  |  |
| C02 | Cada `name` coincide con el nombre de su directorio; no hay nombres duplicados. |  |  |
| C03 | Metadatos locales (`category`, `order`, `tags`, cuando existan) son válidos, coherentes y no duplican valores que deban ser únicos. |  |  |
| C04 | El inventario real coincide con el routing completo; no hay skills huérfanas ni rutas a skills inexistentes. |  |  |
| C05 | El inventario real se compara con todos los catálogos: README de `skills/`, referencia rápida, README raíz y cualquier índice equivalente. |  |  |
| C06 | Todo documento que declare el número de skills coincide con el inventario real o identifica explícitamente un dato histórico. |  |  |
| C07 | `README.md`, `CLAUDE.md` y `docs/ARCHITECTURE.md` describen la misma estructura, conteo, categorías y responsabilidades. |  |  |
| C08 | Los enlaces Markdown locales en `docs/`, `skills/` y documentos raíz existen y resuelven correctamente. |  |  |
| C09 | Referencias, scripts, assets, ejemplos y plantillas declarados por las skills existen, son alcanzables y no apuntan a rutas obsoletas. |  |  |
| C10 | La sintaxis de los artefactos modificados es válida y las pruebas relevantes pasan; la suite completa se ejecuta cuando sea posible. |  |  |
| C11 | No hay secretos, credenciales, datos sensibles ni artefactos no autorizados; se conserva el formato y el diff no contiene errores de espacios. |  |  |
| C12 | Si corresponde a Oracle/APEX, se ejecutan las validaciones de sólo lectura, QA, ambientes y evidencias definidas por el flujo aplicable. |  |  |
| C13 | Si hay SQL nuevo o modificado, pasa el validador de estilo y gobierno Oracle; si no hay SQL, marcar `N/A` y explicar por qué. |  |  |
| C14 | Changelog, decisiones y planes reflejan el cambio, su alcance, riesgos, aprobaciones y resultado. |  |  |
| C15 | Existe evidencia reproducible de auditoría, pruebas, limitaciones conocidas y decisión final de cierre. |  |  |

## Comandos mínimos de cierre

Desde la raíz del repositorio:

```powershell
git diff --check
python .\scripts\audit_skill_ecosystem.py
python -m pytest tests -v
git status --short
```

Para cambios SQL, además:

```powershell
python .\skills\oracle-data-change-governance-final\scripts\validate_sql_style.py <archivo-o-carpeta-sql>
```

Para cambios de Python, PowerShell, configuración o integraciones, ejecute las
validaciones específicas disponibles y registre cuáles no pudieron ejecutarse.
No se puede declarar “completamente validada” una actualización si una
validación obligatoria no pudo ejecutarse.

## Criterio final

El cierre requiere: todos los controles aplicables en `PASS`, todos los
`N/A` justificados, evidencia guardada, limitaciones declaradas y una decisión
final explícita. La auditoría debe comparar siempre el inventario real de skills
con todos los catálogos y documentos que declaran ese inventario; actualizar sólo
el archivo que cambió no satisface esta política.

Esta política gobierna el cierre documental sin modificar las políticas
Oracle/APEX existentes sobre acceso, aprobaciones, seguridad, ambientes, DATA
o SQL.
