# Plan de Implementación: Sistema de URLs por Usuario

## 📋 Objetivo

Implementar un sistema completo de gestión de URLs (local y externa) con permisos por usuario, permitiendo al administrador controlar qué usuarios pueden acceder a cada tipo de URL.

---

## 🎯 Fases de Implementación

### ✅ FASE 0: Planificación y Análisis
- [x] Documento de plan creado
- [x] Requisitos definidos
- [x] Arquitectura diseñada
- [ ] Aprobación del usuario

---

### 📦 FASE 1: Migración de Base de Datos

**Objetivo**: Añadir columnas necesarias a la tabla Users

#### Tareas:
- [ ] 1.1. Crear archivo de migración Alembic
- [ ] 1.2. Añadir columna `allow_local_access` (boolean, default: True)
- [ ] 1.3. Añadir columna `allow_external_access` (boolean, default: False)
- [ ] 1.4. Ejecutar migración en base de datos
- [ ] 1.5. Verificar que las columnas existen

#### Archivos a modificar:
- `app/models/__init__.py` (modelo User)
- Crear: `alembic/versions/XXXX_add_user_url_permissions.py`

#### Verificación:
```sql
SELECT allow_local_access, allow_external_access FROM users LIMIT 1;
```

---

### ⚙️ FASE 2: Configuración Global de URLs

**Objetivo**: Añadir settings para local_url y external_url

#### Tareas:
- [ ] 2.1. Añadir `local_url` a settings en `main.py`
- [ ] 2.2. Añadir `external_url` a settings en `main.py`
- [ ] 2.3. Modificar template `settings.html` para mostrar ambos campos
- [ ] 2.4. Reorganizar layout de Settings (eliminar espacios)
- [ ] 2.5. Añadir validación de URLs en backend
- [ ] 2.6. Actualizar lista de `dynamicKeys` en JavaScript

#### Archivos a modificar:
- `main.py` (inicialización de settings)
- `app/templates/settings.html` (campos de configuración)

#### Valores por defecto:
- `local_url`: `http://localhost:6880` (o IP local detectada)
- `external_url`: `` (vacío por defecto)

---

### 🔧 FASE 3: Lógica de Generación de URLs

**Objetivo**: Modificar `get_base_url()` para usar local_url o external_url según configuración

#### Tareas:
- [ ] 3.1. Crear función `get_local_url()` en `app/api/xtream.py`
- [ ] 3.2. Crear función `get_external_url()` en `app/api/xtream.py`
- [ ] 3.3. Modificar `get_base_url()` para aceptar parámetro `use_external`
- [ ] 3.4. Actualizar todos los endpoints que generan URLs
- [ ] 3.5. Añadir fallback si URLs no están configuradas

#### Archivos a modificar:
- `app/api/xtream.py` (funciones de URL)

#### Lógica:
```python
def get_local_url() -> str:
    # Lee local_url de BD, fallback a Host header
    
def get_external_url() -> str:
    # Lee external_url de BD, fallback a local_url
    
def get_base_url(request: Request, use_external: bool = False) -> str:
    if use_external:
        return get_external_url()
    return get_local_url()
```

---

### 👥 FASE 4: Panel de Gestión de Usuarios

**Objetivo**: Añadir checkboxes de permisos en el panel de usuarios

#### Tareas:
- [ ] 4.1. Añadir checkboxes en modal "Add User"
- [ ] 4.2. Añadir checkboxes en modal "Edit User"
- [ ] 4.3. Modificar endpoint POST `/api/users` para aceptar permisos
- [ ] 4.4. Modificar endpoint PUT `/api/users/{id}` para actualizar permisos
- [ ] 4.5. Mostrar permisos en la tabla de usuarios (iconos o badges)
- [ ] 4.6. Validar que admin siempre tiene ambos permisos

#### Archivos a modificar:
- `app/templates/users.html` (modales y tabla)
- `app/api/users.py` (endpoints de creación/edición)

#### UI en tabla de usuarios:
```
Username | Email | Permissions | Actions
---------|-------|-------------|--------
admin    | ...   | 🏠 🌐      | [Edit] [Delete]
user1    | ...   | 🏠         | [Edit] [Delete]
user2    | ...   | 🌐         | [Edit] [Delete]
```

Leyenda:
- 🏠 = Local Access
- 🌐 = External Access

---

### 🔗 FASE 5: Modal "View URLs" Mejorado

**Objetivo**: Mostrar URLs según permisos del usuario

#### Tareas:
- [ ] 5.1. Modificar función `showUserUrls()` en JavaScript
- [ ] 5.2. Obtener permisos del usuario desde API
- [ ] 5.3. Mostrar sección "Local URLs" si tiene permiso local
- [ ] 5.4. Mostrar sección "External URLs" si tiene permiso externo
- [ ] 5.5. Mostrar ambas secciones para admin
- [ ] 5.6. Añadir badges indicando tipo de acceso
- [ ] 5.7. Mejorar diseño del modal (tabs o secciones)

#### Archivos a modificar:
- `app/templates/users.html` (función showUserUrls)

#### Estructura del modal:
```
┌─────────────────────────────────────┐
│ URLs for User: username             │
├─────────────────────────────────────┤
│ 🏠 Local Access URLs                │
│   M3U: http://192.168.1.50:6880/... │
│   EPG: http://192.168.1.50:6880/... │
│   Xtream: ...                       │
├─────────────────────────────────────┤
│ 🌐 External Access URLs             │
│   M3U: http://iptv.midominio.com/...│
│   EPG: http://iptv.midominio.com/...│
│   Xtream: ...                       │
└─────────────────────────────────────┘
```

---

### 📊 FASE 6: Gestión Masiva de Usuarios

**Objetivo**: Permitir cambiar permisos de múltiples usuarios a la vez

#### Tareas:
- [ ] 6.1. Añadir checkboxes de selección en tabla de usuarios
- [ ] 6.2. Añadir botón "Bulk Actions" en header de tabla
- [ ] 6.3. Crear modal "Bulk Edit Permissions"
- [ ] 6.4. Añadir opciones: Enable Local, Disable Local, Enable External, Disable External
- [ ] 6.5. Crear endpoint POST `/api/users/bulk-update`
- [ ] 6.6. Implementar lógica de actualización masiva
- [ ] 6.7. Mostrar confirmación antes de aplicar cambios
- [ ] 6.8. Proteger admin de cambios masivos

#### Archivos a modificar:
- `app/templates/users.html` (UI de selección masiva)
- `app/api/users.py` (endpoint bulk-update)

#### UI:
```
☑️ Select All | [Bulk Actions ▼]
                  ├─ Enable Local Access
                  ├─ Disable Local Access
                  ├─ Enable External Access
                  └─ Disable External Access
```

---

### 🧪 FASE 7: Pruebas y Validación

**Objetivo**: Verificar que todo funciona correctamente

#### Tareas:
- [ ] 7.1. Probar creación de usuario con permisos
- [ ] 7.2. Probar edición de permisos de usuario
- [ ] 7.3. Probar modal "View URLs" con diferentes permisos
- [ ] 7.4. Probar generación de playlist con local_url
- [ ] 7.5. Probar generación de playlist con external_url
- [ ] 7.6. Probar gestión masiva de usuarios
- [ ] 7.7. Verificar que admin siempre tiene ambos permisos
- [ ] 7.8. Probar con usuario sin permisos (edge case)
- [ ] 7.9. Verificar URLs en diferentes clientes IPTV

#### Casos de prueba:
1. Usuario solo con local → Solo ve URLs locales
2. Usuario solo con externo → Solo ve URLs externas
3. Usuario con ambos → Ve ambas secciones
4. Admin → Siempre ve ambas
5. Usuario sin permisos → Mensaje de error

---

### 📝 FASE 8: Documentación

**Objetivo**: Documentar todos los cambios realizados

#### Tareas:
- [ ] 8.1. Actualizar `MEJORAS-IMPLEMENTADAS.md`
- [ ] 8.2. Actualizar `README.md` (sección de configuración)
- [ ] 8.3. Actualizar `ACCESO.md` (URLs por usuario)
- [ ] 8.4. Crear guía de uso para administradores
- [ ] 8.5. Documentar estructura de permisos
- [ ] 8.6. Añadir ejemplos de configuración

#### Documentos a actualizar:
- `MEJORAS-IMPLEMENTADAS.md`
- `README.md`
- `ACCESO.md`
- Crear: `GUIA-PERMISOS-USUARIOS.md`

---

### 🚀 FASE 9: Despliegue

**Objetivo**: Compilar y desplegar los cambios

#### Tareas:
- [ ] 9.1. Ejecutar migración de base de datos
- [ ] 9.2. Compilar imagen Docker
- [ ] 9.3. Desplegar contenedores
- [ ] 9.4. Verificar logs sin errores
- [ ] 9.5. Verificar health check
- [ ] 9.6. Probar acceso al dashboard
- [ ] 9.7. Verificar que settings se cargan correctamente

#### Comandos:
```bash
# Migración (si usamos Alembic)
docker-compose exec unified-acestream alembic upgrade head

# Compilación y despliegue
docker-compose down
docker-compose build
docker-compose up -d

# Verificación
docker-compose ps
docker-compose logs unified-iptv --tail 50
curl http://localhost:6880/health
```

---

## 📊 Resumen de Cambios

### Base de Datos
- ✅ Tabla `users`: +2 columnas (allow_local_access, allow_external_access)
- ✅ Tabla `settings`: +2 registros (local_url, external_url)

### Backend (Python)
- ✅ `app/models/__init__.py`: Modelo User actualizado
- ✅ `app/api/xtream.py`: Funciones de URL mejoradas
- ✅ `app/api/users.py`: Endpoints con permisos
- ✅ `main.py`: Inicialización de settings

### Frontend (HTML/JS)
- ✅ `app/templates/settings.html`: Campos de URLs
- ✅ `app/templates/users.html`: Permisos y gestión masiva

### Documentación
- ✅ `MEJORAS-IMPLEMENTADAS.md`
- ✅ `README.md`
- ✅ `ACCESO.md`
- ✅ `GUIA-PERMISOS-USUARIOS.md` (nuevo)

---

## 🎯 Criterios de Éxito

- [ ] Admin puede configurar local_url y external_url en Settings
- [ ] Admin puede asignar permisos (local/externo) a cada usuario
- [ ] Usuarios solo ven URLs según sus permisos
- [ ] Admin siempre ve ambas URLs
- [ ] Gestión masiva funciona correctamente
- [ ] URLs se generan correctamente según configuración
- [ ] Clientes IPTV pueden conectarse con ambas URLs
- [ ] Documentación completa y actualizada

---

## ⚠️ Notas Importantes

1. **Migración de BD**: Usuarios existentes tendrán `allow_local_access=True` y `allow_external_access=False` por defecto
2. **Admin protegido**: El usuario admin SIEMPRE tiene ambos permisos (no se pueden desactivar)
3. **Fallback**: Si local_url no está configurado, usa Host header del request
4. **Validación**: URLs deben empezar con http:// o https://
5. **Compatibilidad**: Sistema funciona sin configurar external_url (solo local)

---

## 🔄 Estado Actual

**Fase actual**: FASE 0 - Esperando aprobación

**Última actualización**: 25 de enero de 2026

---

## ✅ Aprobación

- [ ] Plan revisado por el usuario
- [ ] Arquitectura aprobada
- [ ] Listo para comenzar implementación

**Firma**: _________________  
**Fecha**: _________________

