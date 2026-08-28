# Guía canónica para crear una nueva skill

Esta guía define el procedimiento obligatorio para que una nueva skill nazca
alineada con el estándar portable de Agent Skills y con las convenciones de
`apex.skills`. La fuente de autoridad para el cierre sigue siendo la [política
canónica de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md).

## 1. Decidir si debe existir una skill nueva

Antes de crear archivos:

1. Describe la necesidad en una frase orientada al usuario.
2. Revisa el inventario real en `skills/*/SKILL.md`, el routing y los catálogos.
3. Comprueba si una skill existente puede cubrir el caso mediante una
   referencia, un procedimiento adicional o una combinación de routing.
4. Crea una skill nueva sólo si la separación mejora el descubrimiento, la
   seguridad, los permisos, la responsabilidad o la mantenibilidad.
5. Registra objetivo, alcance, alternativas descartadas, dependencias, riesgos,
   permisos, compatibilidad, pruebas, rollback y descontinuación, si aplica.

No se debe crear una skill sólo para duplicar una existente, separar un caso de
uso demasiado pequeño o introducir una preferencia de un agente concreto.

## 2. Contrato portable y estructura

La estructura mínima es:

```text
skills/<nombre-de-skill>/
└── SKILL.md
```

El directorio puede añadir `references/`, `scripts/`, `assets/`, plantillas o
`agents/openai.yaml` sólo cuando sean necesarios y estén documentados.

El `SKILL.md` debe comenzar con frontmatter YAML válido:

```yaml
---
name: apex-nueva-capacidad
description: Resuelve una intención concreta de Oracle APEX con alcance claro.
---
```

Requisitos portables:

- `name` es único, coincide exactamente con el directorio, usa minúsculas y
  kebab-case, y no contiene aliases ambiguos.
- `description` explica qué resuelve, cuándo debe descubrirse y cuáles son sus
  límites. Debe usar lenguaje que el usuario emplearía, no sólo el nombre
  técnico de la skill.
- El cuerpo contiene las instrucciones esenciales, ordenadas para lectura
  progresiva: primero `SKILL.md`, luego recursos sólo cuando la tarea los
  necesite.
- Las rutas y enlaces portables son relativos al recurso que los declara y
  deben existir.
- La skill declara límites de acceso, aprobaciones, datos sensibles y
  condiciones de bloqueo cuando corresponda.

Convenciones adicionales de este repositorio:

- `category` debe ser coherente con las categorías existentes.
- `order` debe ser un entero único y revisarse contra el inventario actual.
- `tags` debe describir descubrimiento, flujo y nivel de acceso.
- `agents/openai.yaml` es específico del agente y no puede cambiar el
  significado ni las restricciones de la skill portable.

Plantilla recomendada:

```markdown
---
name: apex-nueva-capacidad
category: "Apex [Categoría]"
order: <entero disponible>
tags: ["tema", "flujo", "acceso"]
description: "Descripción orientada a la intención del usuario y al alcance"
---

# Título de la skill

## Propósito

Qué problema resuelve y qué queda fuera de alcance.

## Cuándo usarla

Intenciones, palabras y artefactos que deben descubrirla.

## Flujo

1. Validación inicial y precondiciones.
2. Análisis o ejecución autorizada.
3. Evidencia, resultado y condiciones de bloqueo.

## Seguridad y límites

Permisos, ambientes, datos sensibles, aprobaciones y rollback.

## Referencias

Enlaces a documentos locales necesarios.
```

## 3. Integración en el ecosistema

Después de crear el `SKILL.md`, actualiza en el mismo cambio:

1. `skills/apex/references/routing.md`, sólo con la ruta mínima necesaria.
2. `skills/README.md` y `skills/SKILLS-QUICK-REFERENCE.md`.
3. `README.md`, `CLAUDE.md` y `docs/ARCHITECTURE.md` si describen inventario,
   categorías, estructura o responsabilidades afectadas.
4. `docs/ACTUALIZACION-ECOSISTEMA.md` o la documentación especializada cuando
   cambie un criterio de gobierno.
5. `CHANGELOG.md`.
6. Decisiones y plan del proyecto, con evidencia y limitaciones.
7. Pruebas nuevas o actualizadas para metadatos, routing, seguridad o scripts,
   según el comportamiento agregado.

No dejes una skill huérfana en los catálogos ni agregues una ruta que no tenga
un `SKILL.md` correspondiente. El inventario de `skills/*/SKILL.md` es la
fuente de verdad; los documentos deben reflejarlo.

## 4. Validación antes de publicar

Desde la raíz del repositorio, ejecuta como mínimo:

```powershell
python .\scripts\apex_metadata.py validate skills\apex-nueva-capacidad\SKILL.md
python .\scripts\audit_skill_ecosystem.py
python .\scripts\audit_quality_score.py
python -m pytest tests -v
git diff --check
git status --short
```

También revisa manualmente nombres duplicados, `order`, categorías, tags,
conteos, routing, índices, enlaces, scripts, assets y plantillas. Revisa
además secretos, credenciales, datos reales, permisos, compatibilidad entre
agentes y sistemas operativos, y procedencia/licencia de material externo.

Un `FAIL` bloquea el cierre. Todo `N/A` requiere una justificación concreta.
Si se agrega o modifica SQL, ejecuta además el validador de estilo y gobierno
Oracle correspondiente.

## 5. Revisión y publicación

La skill modificada no puede ser su único juez. Antes de publicar:

1. conserva la evidencia reproducible de comandos y resultados;
2. solicita revisión humana o de un agente externo al componente modificado;
3. confirma que los cambios no revierten trabajo existente;
4. documenta riesgos residuales, rollback y decisión final;
5. publica sólo cuando todos los controles aplicables estén en `PASS`.

Para la contribución Git, sigue [`CONTRIBUTING.md`](CONTRIBUTING.md) y usa la
plantilla de pull request.
