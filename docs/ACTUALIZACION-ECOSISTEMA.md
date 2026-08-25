# Protocolo de actualización del ecosistema APEX Skills

Este protocolo es obligatorio cuando se agrega, elimina o cambia una skill, un upstream, un
script, una referencia de Oracle APEX, una política de seguridad o un flujo de entrega. Su objetivo
es que una actualización sea coherente, descubrible, auditable y reversible.

## Alcance y evidencia inicial

1. Registre el objetivo, alcance, riesgo, responsable, fecha y decisiones en el espacio de
   proyecto correspondiente.
2. Revise `git status`, la rama activa y los cambios remotos antes de editar.
3. Para cada upstream, registre URL, propietario, licencia, rama o tag, commit SHA, fecha de
   recuperación, versión objetivo de APEX y la clasificación **adopt**, **adapt** o
   **reference only**. Consulte [UPSTREAMS.md](UPSTREAMS.md).
4. No incorpore secretos, muestras de datos, application/workspace IDs, privilegios, SQL de negocio
   ni dependencias de plug-ins sin revisión explícita.

## Implementación y coherencia

1. Cada skill nueva debe incluir `SKILL.md` con front matter válido (`name`, `category`, `order`,
   `tags`, `description`) y, cuando el agente la exponga, `agents/openai.yaml`.
2. Actualice el coordinador `skills/apex/references/routing.md` con la intención del usuario y el
   flujo especialista más pequeño que la resuelva.
3. Actualice ambos catálogos: `skills/README.md` y `skills/SKILLS-QUICK-REFERENCE.md`; ajuste el
   total de skills, categorías y decisiones rápidas cuando corresponda.
4. Actualice las skills relacionadas para que el nuevo flujo sea invocable desde diseño, QA,
   seguridad y entrega, sin duplicar autoridad ni alterar aprobaciones.
5. Actualice los documentos de upstream y seguridad cuando cambie la procedencia, licencia,
   compatibilidad o política de reutilización.
6. Para scripts o comportamiento automatizado, agregue pruebas unitarias o de integración
   proporcionales al riesgo y actualice la documentación de uso.

## Validación obligatoria

Ejecute desde la raíz del repositorio antes de entregar o abrir una PR:

```powershell
python .\scripts\audit_skill_ecosystem.py
python -m pytest tests -v
git diff --check
git status --short
```

La auditoría verifica recursos canónicos y enlaces Markdown locales en `docs/` y `skills/`.
Un resultado `AUDIT_FAIL`, una prueba fallida o una diferencia con espacios inválidos bloquea la
entrega. Cuando se modifique Python, ejecute además las comprobaciones aplicables configuradas por
el repositorio: Black, isort, flake8, mypy, Bandit y detección de secretos.

## Revisión de entrega

Confirme como mínimo:

- no hay enlaces rotos, skills huérfanas ni rutas faltantes;
- las skills nuevas aparecen en el enrutador y en ambos catálogos;
- los flujos de lectura siguen sin efectuar cambios y los de escritura conservan aprobaciones;
- se declaró la versión APEX compatible y las dependencias del upstream;
- se preservaron avisos de licencia y no hay secretos, datos sensibles ni datos de ejemplo no
  aprobados;
- existe evidencia de pruebas y auditoría; y
- se actualizó `CHANGELOG.md` si el cambio afecta capacidades disponibles para usuarios.

## Patrón oficial: evaluación antes de adopción

Para cada ejemplo oficial de Oracle APEX, seleccione una versión compatible y evalúe un único
patrón por vez. Genere una ficha con: objetivo, procedencia, dependencias de esquema, roles,
artefactos APEX, seguridad, rendimiento, adaptación necesaria, pruebas y decisión final. No
importe el ejemplo completo como sustituto de la ficha ni lo promueva sin validación en un entorno
no productivo.

