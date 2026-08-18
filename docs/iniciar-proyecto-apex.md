# Iniciar un proyecto Oracle APEX

Use este flujo para crear una aplicación nueva o agregar páginas a una existente. La base técnica es Oracle APEX 24.1.3 y las operaciones de producción son de solo lectura por defecto.

## 1. Definir el alcance

Antes de modificar APEX, registre:

```text
Aplicación: nombre y App ID (si ya existe)
Ambiente: Desarrollo o TEST
Objetivo: aplicación nueva / páginas nuevas / mejora de páginas existentes
Usuarios, roles y autorizaciones
Tablas, vistas, paquetes y APIs involucrados
Páginas, navegación y resultados esperados
Criterios de aceptación y datos de prueba
```

No autorice cambios en producción como parte de este paso.

## 2. Crear el repositorio de la aplicación

Mantenga la aplicación y sus evidencias separadas del repositorio de skills:

```text
mi-nueva-aplicacion/
├─ app/
│  └─ exports/
├─ docs/
├─ evidence/
└─ .gitignore
```

Excluya siempre `.env`, wallets, `tnsnames.ora`, tokens y contraseñas.

## 3. Activar las skills

Indique al agente que use las skills canónicas de este proyecto:

```text
Usa las skills:
- <ruta-a-apex.skills>/skills/apex-engineering-safe
- <ruta-a-apex.skills>/skills/apex-export-qa-safe

Objetivo: desarrollar Oracle APEX 24.1.3.
Regla: no ejecutar cambios en producción. Trabajar únicamente en Desarrollo o TEST.
```

Use también las skills de minería de patrones y diseño cuando estén disponibles en este repositorio.

## 4. Configurar MCP opcionalmente

Configure `apex-mcp` para el cliente de IA usado y compruebe primero estado, conexión, workspace y aplicaciones disponibles. Para cambios autorizados, active `dry-run` antes de ejecutar operaciones que modifiquen APEX.

No almacene secretos en el archivo MCP que se vaya a versionar. Cárguelos desde el almacén de secretos o el entorno local del cliente.

## 5. Analizar antes de construir

Use primero un prompt de análisis:

```text
Analiza el esquema y la aplicación APEX objetivo en modo solo lectura.
Propón el diseño de las páginas, navegación, regiones, items, procesos,
autorizaciones y validaciones. No ejecutes cambios todavía.
```

Revise el diseño, el alcance y el impacto sobre componentes existentes antes de aprobar la implementación.

## 6. Implementar por incrementos pequeños

Ejemplo para páginas nuevas:

```text
En el ambiente TEST, crea las páginas 10 y 11 para gestionar Proveedores:
- Página 10: reporte interactivo con filtros.
- Página 11: formulario modal para crear y editar.
- Usa la tabla DATA.PROVEEDORES.
- Respeta autenticación, autorización y Universal Theme 42.
- Antes de cambiar, muestra el plan y usa dry-run.
- No modifiques componentes fuera del alcance.
```

Para una aplicación nueva:

```text
Quiero crear una nueva aplicación Oracle APEX 24.1.3 en TEST.

Nombre: Gestión de Proveedores
Esquema: DATA
Usuarios: Compras y Administradores
Páginas:
1. Inicio con indicadores
10. Listado de proveedores
11. Formulario de proveedor
20. Reporte de evaluación
9999. Administración

Primero inspecciona el esquema en modo solo lectura y genera una propuesta
de arquitectura, navegación, roles, páginas, componentes y validaciones.
No crees la aplicación ni modifiques la base hasta que apruebe el diseño.
```

## 7. Exportar, validar y versionar

Después de una implementación aprobada en Desarrollo o TEST, exporte la aplicación, guarde el ZIP en `app/exports/` y ejecute el QA estático:

```powershell
python <ruta-a-apex.skills>\skills\apex-export-qa-safe\scripts\validate_export.py .\app\exports\fXXX.zip
```

El resultado `STATIC_PASS` valida la estructura y configuraciones declaradas del export. Complete además pruebas funcionales, de autorización, navegación y datos de prueba antes de promover un cambio.

## Principios de trabajo

- Versione los exportes desde el primer día.
- Mantenga cada página o flujo como una tarea pequeña y verificable.
- Presente un plan antes de cambios estructurales.
- No reutilice IDs internos entre aplicaciones.
- Diferencie evidencia estática, técnica y funcional.
