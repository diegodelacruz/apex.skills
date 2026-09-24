# Configuración de apex.skills para Claude Code

Antes de modificar este repositorio, Claude Code debe leer y cumplir [la política canónica de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md). Ningún archivo puede obligar técnicamente a un agente externo arbitrario; la política se refuerza mediante adaptadores, hooks, CI y revisión independiente.

## Descripción General

Esta guía cubre la configuración de **apex.skills** para usarlo con **Claude Code** (la interfaz de agentes de Anthropic). A diferencia de Codex CLI, Claude Code proporciona acceso automático al MCP (Model Context Protocol) sin configuración manual de conexiones.

## Requisitos Previos

- Claude Code instalado (web, CLI, desktop, o extensión IDE)
- Python 3.13
- Acceso a Oracle APEX 24.1.3 y Oracle Database
- Credenciales de base de datos (usuario/contraseña/DSN)

## Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/diegodelacruz/apex.skills.git
cd apex.skills
```

## Paso 2: Crear el Entorno Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Paso 3: Configurar Credenciales APEX

Usa el script de gestión de credenciales para almacenar de forma segura tus perfiles de APEX:

```bash
python3 scripts/manage_apex_credentials.py set --environment production
# Ingresa:
# - Oracle user: (tu usuario)
# - Oracle password: (tu contraseña)
# - Oracle DSN: (host:puerto/sid)
```

Las credenciales se guardan en el almacén seguro del sistema operativo (Keyring en Linux/macOS, Credential Manager en Windows).

### Validar la Configuración

```bash
python3 scripts/manage_apex_credentials.py validate --environment production
```

## Paso 4: Inicializar los Upstreams Administrados

Los upstreams (apex-mcp, zaimella-skill, zaimella-apex-oracle) se deben inicializar una sola vez:

### En Linux/macOS:

```bash
# Requiere PowerShell 7+ instalado
pwsh scripts/Initialize-ApexSkillUpstreams-V2.ps1
```

### En Windows:

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
```

## Paso 5: Configurar Claude Code para Acceso MCP

### Opción A: Configuración Web (claude.ai/code)

1. Abre [claude.ai/code](https://claude.ai/code)
2. Importa este repositorio como proyecto
3. Claude Code detectará automáticamente los scripts Python y skills disponibles
4. Los skills aparecerán en el panel izquierdo bajo "Skills"

### Opción B: Configuración CLI

```bash
claude-code add-project /ruta/a/apex.skills
```

### Opción C: Configuración de Extensión IDE

Si usas la extensión de Claude Code en VS Code o JetBrains:

1. Abre la carpeta apex.skills como proyecto
2. Claude Code reconocerá automáticamente los skills
3. Usa `/skill-doctor` para verificar la configuración

## Paso 6: Verificar la Instalación

Ejecuta la auditoría de skills para confirmar que todo está configurado correctamente:

```bash
python3 scripts/audit_skill_ecosystem.py
```

Deberías ver: `AUDIT_PASS: required resources and local Markdown links are valid`

## Uso de Skills con Claude Code

### Invocación Automática

Los skills se invocaban automáticamente según el contexto Oracle/APEX detectado. Con Claude Code, puedes:

1. **Mencionarlos explícitamente**: "¿Puedes usar apex-export-qa-safe para validar esta exportación?"
2. **Dejarlos que se activen automáticamente**: El coordinador detecta cambios en archivos APEX y activa skills relevantes
3. **Acceder por slash commands**: `/skill apex-project-bootstrap-final`

### Skills Disponibles

| Skill | Propósito | Activación |
|-------|-----------|-----------|
| `apex-project-bootstrap-final` | Iniciar nuevos proyectos APEX | Manual o archivo APEX detectado |
| `apex-delivery-lifecycle-safe` | Gestionar ciclo de vida de entrega | Manual o cambios TEST→Producción |
| `apex-export-qa-safe` | Validar exportaciones APEX | Manual o ZIP detectado |
| `apex-database-diagnostics` | Diagnosticar problemas DB | Manual o error detectado |
| `oracle-data-change-governance-final` | Gobernar cambios en datos | Manual o cambios DATA detectados |

Consulta `skills/README.md` para la lista completa.

## Comparación: Codex CLI vs Claude Code

| Aspecto | Codex CLI | Claude Code |
|---------|-----------|-------------|
| **Instalación** | Setup manual de MCP | Automático |
| **Credenciales** | Archivo .env | Keyring del SO |
| **Skills** | Invocación explícita | Automática + manual |
| **Interfaz** | Terminal | Web/IDE/Desktop |
| **Escalabilidad** | Monousuario | Multiusuario |
| **Depuración** | Logs en stdout | Logs en panel |

## Troubleshooting

### "ModuleNotFoundError: No module named 'keyring'"

```bash
pip install -r requirements.txt
```

### "No functional APEX workspace was found"

- Verifica que tu usuario tiene acceso a workspaces APEX
- Ejecuta en Oracle SQL Developer:
  ```sql
  SELECT workspace_id, workspace FROM apex_workspaces WHERE workspace <> 'INTERNAL';
  ```

### "Unsupported upstream revision"

Los upstreams pueden haber cambiado. Actualiza con:

```bash
pwsh scripts/Update-ApexSkillUpstreams-V2.ps1
```

### "Skills no aparecen en Claude Code"

1. Ejecuta `audit_skill_ecosystem.py` (ver Paso 6)
2. Recarga Claude Code (F5 o Cmd+R)
3. Verifica que `.mcp.json.example` está en la raíz

## Integración con CI/CD

Los scripts de validación se pueden integrar en CI/CD:

```bash
# En GitHub Actions
- name: Audit Skills
  run: python3 scripts/audit_skill_ecosystem.py

- name: Run Tests
  run: pytest tests/ --cov=scripts --cov=skills
```

## Soporte

- **Documentación**: Ver `docs/`
- **Ejemplos**: Ver `apps/` para exportaciones de ejemplo
- **Testing**: Ejecuta `pytest tests/` para validación completa

## Licencia

Consulta `LICENSE` para términos de uso.
