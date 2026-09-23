---
name: apex-external-context-learn
category: "Apex External Context & Learning"
order: 3.5
tags: ["external-context", "learning", "no-clone", "reference", "read-only", "discovery"]
description: "Learn from external repositories (GitHub or local) without cloning. Create persistent, reusable reference context for APEX engineering workflows."
---

# Apex External Context Learn

## Propósito

Permite analizar y aprender de repositorios externos (públicos de GitHub o carpetas locales) sin necesidad de clonarlos. El aprendizaje se guarda como referencia reutilizable en `control-proyecto/external-repos/` para que otras skills accedan automáticamente al contexto extraído.

**Alcance:**
- Repositorios GitHub públicos (HTTPS sin autenticación)
- Carpetas locales accesibles en el filesystem
- Análisis agnóstico: extrae lo que el usuario solicita
- Persistencia mediante JSONs indexados para acceso rápido

**Fuera de alcance:**
- Clonación de repositorios completos
- Contenido binario o assets
- Repositorios privados sin autenticación explícita
- Análisis automático sin solicitud del usuario

---

## Cuándo usarla

**Intenciones de usuario:**
- "Aprende de [URL/ruta] qué patrones usa para..."
- "Analiza el repositorio en [ruta] y extrae..."
- "Basándote en [proyecto], ¿cuál es la arquitectura de..."
- "Necesito contexto de [repo] para esta tarea"

**Artefactos que la descubren:**
- Solicitud de análisis de código/arquitectura desde proyectos externos
- Peticiones que requieren referencia a implementaciones similares
- Validación de patrones contra proyectos de producción
- Contexto técnico para decisiones de diseño

**Palabras clave:**
- learn, learn from, extract from, analyze, understand, pattern
- external, repository, repo, GitHub, local project, reference

---

## Flujo

### 1. Validación Inicial

```
┌─────────────────────────────────────────┐
│ Usuario proporciona:                    │
│ - URL (GitHub) o ruta (local)          │
│ - Qué quiere aprender/extraer          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ Validar:                                │
│ ✓ URL accesible o ruta existe           │
│ ✓ No está vacía                         │
│ ✓ Puede leerse sin autenticación        │
└────────────┬────────────────────────────┘
             │
         NO ◄─┘─► SÍ
         │          │
         ▼          ▼
      ERROR      [2. Análisis]
```

### 2. Análisis de Repositorio

- **Estructuración:** Mapeo de directorios, tipos de archivos, lenguajes detectados
- **Extracción agnóstica:** Procesa según lo que el usuario solicitó
- **Resumen:** Genera síntesis de hallazgos sin guardar contenido completo
- **Metadatos:** Captura fecha, versión (commit SHA si es GitHub), estructura

### 3. Persistencia y Referencia

```json
control-proyecto/external-repos/
├── external-repos-index.json           # Index central (lista rápida)
├── github-user-repo-A.json             # Un JSON por proyecto
├── github-user-repo-B.json
└── local-project-C.json
```

**Estructura JSON por proyecto:**
```json
{
  "identifier": "github-user-repo-A",
  "source": "https://github.com/user/repo",
  "source_type": "github_url|local_path",
  "scanned_at": "2026-09-23T17:03:21Z",
  "repo_info": {
    "description": "[si está en README]",
    "languages_detected": ["Python", "SQL", "JavaScript"],
    "file_extensions_found": [".py", ".sql", ".js", ".md"],
    "total_files": 47,
    "structure_summary": "app/ (8 files), tests/ (12 files), docs/ (5 files), ..."
  },
  "learning_summary": {
    "extracted_by_user": "¿Patrones de BD?",
    "analysis": "[resumen de lo extraído]",
    "key_findings": ["finding 1", "finding 2"]
  },
  "version_hash": "[commit SHA si es GitHub]"
}
```

### 4. Resultado y Distribución

- **Confirmación:** Usuario ve summary + ubicación en `external-repos/`
- **Contexto automático:** Otras skills leen JSONs sin solicitud explícita
- **Referencia explícita:** Usuario puede citar en solicitudes posteriores
- **Reutilización:** Mismo repo → consulta local, evita re-análisis

---

## Seguridad y Límites

### Permisos y Acceso

- **GitHub:** HTTPS público, sin token requerido
- **Local:** Lectura solo dentro de rutas accesibles al usuario
- **Sin credenciales:** No se almacenan tokens, claves API o autenticación

### Datos Sensibles

**NO guardar:**
- Contenido completo de archivos (solo estructura y resumen)
- Credenciales, keys, secrets (ignorar patrones `.env`, `config.secret.*`)
- Archivos binarios o medios grandes
- Información personal de repositorios privados

**SÍ guardar:**
- Metadatos públicos (estructura, lenguajes, extensiones)
- Resúmenes de análisis (lo que el usuario pidió extraer)
- Referencias de versión (commit SHA, dates)
- Índices para búsqueda rápida

### Manejo de Errores

| Error | Acción |
|-------|--------|
| URL no existe / no responde | Informar al usuario, NO guardar |
| Repositorio vacío | Informar: "Repositorio vacío, nada que aprender" |
| Acceso denegado (404, 403) | Informar: "No se puede acceder [razón]" |
| Ruta local no existe | Informar: "Ruta no accesible" |
| Repo ya aprendido | Preguntar: "¿Volver a analizar? [y/n]" |

### Rollback y Descontinuación

- **Borrar aprendizaje:** Usuario confirma, se elimina JSON + actualiza index
- **No permite:** Sobreescribir sin confirmación; perder análisis previos

---

## Integración con Ecosistema

### Consumo por otras Skills

Otras skills (engineering-safe, solution-design, code-generation-safe) leen automáticamente:

```python
# En otra skill:
from scripts.external_repo_indexer import ExternalRepoIndexer

indexer = ExternalRepoIndexer()
repos = indexer.list_all()  # Lee external-repos-index.json

if repos:
    context = indexer.get_context(repo_id)  # Inyecta en análisis
    # Usa context para validar patrones, generar código, diseñar
```

### Referencias Explícitas

Usuario puede citar:
```
"Valida esta estructura contra lo que aprendimos del proyecto github-user-repo-A"
→ Skill busca en external-repos/ → aplica contexto
```

### Actualización y Re-análisis

- Primera invocación: Analiza y guarda
- Próxima invocación del mismo repo: Consulta local
- Usuario explícito: "re-analiza github-user-repo-A" → borra + vuelve a guardar

---

## Procedimiento: Paso a Paso (si usuario elige)

Si el usuario pide `--paso-a-paso` o no especifica iteración:

1. **Validar acceso**
   ```
   ✓ Accediendo a [URL/ruta]...
   ```

2. **Escanear estructura**
   ```
   ✓ Encontrados 47 archivos en 8 directorios
   ✓ Lenguajes: Python (60%), SQL (25%), JavaScript (15%)
   ```

3. **Extraer análisis**
   ```
   ✓ Análisis de [lo que pidió]: [resumen]
   ```

4. **Guardar referencia**
   ```
   ✓ Guardado en: control-proyecto/external-repos/github-user-repo-A.json
   ✓ Index actualizado: external-repos-index.json
   ```

5. **Confirmar disponibilidad**
   ```
   ✓ Disponible para otras skills automáticamente
   ✓ Cita explícita: "valida contra github-user-repo-A"
   ```

---

## Referencias

- [Guía canónica de skills](../../docs/GUIA-CREAR-NUEVA-SKILL.md)
- [Política de evolución del ecosistema](../../docs/POLITICA-EVOLUCION-ECOSISTEMA.md)
- [External Repos Indexer](../../scripts/external_repo_indexer.py)
- [External Repos Scanner](../../scripts/external_repo_scanner.py)
