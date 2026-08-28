# Inicialización en Windows - Guía Paso a Paso

## El Error Que Obtuviste

```
ERROR: Unsupported upstream revision: expected code not found in
D:\Users\ddelacruz\Desktop\Python\codex\apex.skills\.upstreams\managed\apex-mcp\apex_mcp\db.py
```

## ¿Por Qué Ocurrió?

Intentaste ejecutar `Initialize-ApexCodexProject.ps1` **sin haber descargado primero los upstreams administrados**. El script necesita estos tres repositorios:

- `TechFernandesLTDA/apex-mcp` - Servidor MCP para inspección
- `jefersonKel/zaimella-skill` - Estándares y utilidades
- `zaimella/zaimella-apex-oracle` - Referencia de versiones

## ✅ Solución Paso a Paso

### 1. **Abre PowerShell como Administrador**

```powershell
# Navega a la raíz del repositorio apex.skills
cd D:\Users\ddelacruz\Desktop\Python\codex\apex.skills
```

### 2. **Descarga los Upstreams** (Este paso es REQUERIDO)

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
```

**Esto descargará:**
- `.upstreams\managed\apex-mcp\` (necesario para el parche)
- `.upstreams\managed\zaimella-skill\`
- `.upstreams\managed\zaimella-apex-oracle\`

### 3. **Después de descargados los upstreams, inicializa el proyecto**

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -InstallSharedDependencies
```

**Opciones:**
- `-ProjectPath "D:\ruta\a\tu\proyecto"` - Si el proyecto está en otra ubicación
- `-InstallSharedDependencies` - Para instalar Python y dependencias (primera vez)

### 4. **Verifica la instalación**

```powershell
codex mcp list
```

Deberías ver `apex-mcp-test` en la lista.

---

## 📋 Orden Correcto de Ejecución

```
1. Initialize-ApexSkillUpstreams-V2.ps1       ← PRIMERO
   └─ Descarga upstreams (.upstreams/)

2. Initialize-ApexCodexProject.ps1           ← SEGUNDO
   └─ Configura TEST profile
   └─ Instala skills
   └─ Registra MCP en Codex

3. Abre Codex CLI o Codex Desktop
   └─ En el proyecto que inicializaste
```

---

## 🔍 Verificación: ¿Están los Upstreams Descargados?

Si necesitas verificar que los upstreams están presentes:

```powershell
# Verifica que apex-mcp existe
Test-Path ".\\.upstreams\\managed\\apex-mcp\\apex_mcp"

# Si devuelve True: ✅ OK
# Si devuelve False: ❌ Necesitas ejecutar Initialize-ApexSkillUpstreams-V2.ps1
```

---

## ⚠️ Problemas Comunes en Windows

### A. "Python command failed"
**Causa:** Python no está instalado o no está en PATH.
**Solución:** Ejecuta con `-InstallSharedDependencies` para crear el entorno virtual.

### B. "Could not install APEX skills for Codex CLI"
**Causa:** Codex CLI no está disponible.
**Solución:** Instala Codex CLI primero, o usa Claude Code en su lugar.

### C. "Could not register apex-mcp-test in Codex"
**Causa:** El MCP anterior existe pero está mal configurado.
**Solución:** Ejecuta en Codex:
```
codex mcp remove apex-mcp-test
```
Luego vuelve a ejecutar el inicializador.

---

## 💡 Alternativa: Usar Claude Code en lugar de Codex CLI

Si prefieres Claude Code (recomendado en Windows):

1. Ejecuta solo: `Initialize-ApexSkillUpstreams-V2.ps1`
2. Abre el proyecto en Claude Code
3. Sigue las instrucciones en `docs/setup-claude-code.md`

---

## 📞 ¿Sigue Fallando?

Incluye esta información al reportar:

```powershell
# 1. Estado de upstreams
Test-Path ".\.upstreams\managed\apex-mcp"
Test-Path ".\.upstreams\managed\zaimella-skill"
Test-Path ".\.upstreams\managed\zaimella-apex-oracle"

# 2. Versión de Python
python --version

# 3. Estado de Codex
codex --version
codex mcp list
```

---

**Última actualización:** 2026-08-20
**Sistema operativo:** Windows 10/11
**PowerShell versión:** 5.0+
