# Plan: snapshots y setup resiliente

## Pasos

1. Empaquetar snapshots ZIP de los tres upstreams administrados, verificar SHA-256 y registrar URL, rama, commit, propósito y licencia en `vendor/upstreams/manifest.json`.
2. Preservar el diff local preexistente de `apex-mcp` en un overlay separado y aplicarlo sólo después de verificar su hash.
3. Implementar sincronización: validar snapshot/lock, extraer en staging, consultar ramas remotas, comprobar fast-forward y overlay, probar la wheel de `apex-mcp`, respaldar antes del reemplazo y mantener la copia activa si falla la red o una validación.
4. Integrar la sincronización en `Setup-ApexSkills.ps1` y hacer que `Initialize-ApexCodexProject.ps1` invoque el setup, para que no se necesite repetir comandos.
5. Alinear la política, el README y las guías de upstreams con el nuevo flujo.
6. Validar parseo PowerShell, snapshots y overlay en modo `-WhatIf -Offline`; ejecutar auditoría de ecosistema, seguridad y pruebas aplicables sin tocar las copias activas `.upstreams`.

## Evidencia inicial

- Tres snapshots administrados locales existían en los commits fijados por el lock.
- `apex-mcp` tenía siete archivos con modificaciones locales esperadas; no había archivos sin seguimiento.
- Las copias `zaimella-skill` y `zaimella-apex-oracle` estaban limpias y no declaraban licencia en archivos `LICENSE`, `COPYING` o `NOTICE`.
- Las dos ramas anteriores mostraban avances remotos al 2026-09-23; la implementación no hará fetch/merge contra los checkouts existentes.
- Los snapshots de referencia opcionales se excluyen del setup normal.

## Criterios de aceptación

- Clonación nueva: los snapshots permiten preparar los tres upstreams incluso sin red.
- Remoto no disponible: el setup continúa con la copia activa/snapshot y reporta qué origen utilizó.
- Avance remoto: backup verificable antes de activar, sólo fast-forward y overlay aplicable.
- Fallo de compilación: no se activa el candidato remoto; se conserva la copia anterior y se compila esa copia.
- Copia local modificada fuera del overlay esperado: se conserva y se omite el reemplazo automático.
- Una sola ejecución del inicializador resuelve upstreams, Python, dependencias y skills antes de validar el proyecto.
- Sin conexión Oracle adicional, mutación APEX ni registro MCP por la sincronización.
