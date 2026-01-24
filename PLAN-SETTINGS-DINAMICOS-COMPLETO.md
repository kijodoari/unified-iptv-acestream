# Plan de Implementación: Settings Dinámicos Completos

## 📊 Resumen Ejecutivo

**Estado**: ✅ IMPLEMENTACIÓN COMPLETADA

**Logros**:
- ✅ 22 settings totales (eliminados 2 obsoletos: scraper_urls, epg_sources)
- ✅ 9 settings dinámicos (se aplican sin reiniciar)
- ✅ 13 settings que requieren restart
- ✅ Gestión profesional de URLs (ScraperURL y EPGSource)
- ✅ APIs REST completas para gestión de fuentes
- ✅ Servicios leen de tablas en lugar de settings

**Resultado**: Sistema completamente funcional con configuración dinámica y gestión profesional de URLs.

---

## 🎯 Objetivo

Hacer que TODOS los settings sean reales y utilizables, con la capacidad de cambiar valores dinámicamente sin reiniciar el servidor cuando sea técnicamente posible.

## 📋 Alcance del Proyecto

### Parte 1: Settings Dinámicos (6 valores)
Hacer que estos settings se lean dinámicamente y se apliquen sin reiniciar:
1. ✅ `scraper_update_interval` - YA IMPLEMENTADO
2. ✅ `epg_update_interval` - YA IMPLEMENTADO
3. ✅ `server_timezone` - YA IMPLEMENTADO
4. ⏳ `epg_cache_file` - Por implementar
5. ⏳ `acestream_timeout` - Por implementar
6. ⏳ `acestream_chunk_size` - Por implementar
7. ⏳ `acestream_empty_timeout` - Por implementar
8. ⏳ `acestream_no_response_timeout` - Por implementar
9. ⏳ `access_token_expire_minutes` - Por implementar

### Parte 2: Gestión Profesional de URLs
Reemplazar los settings de texto plano por gestión individual de URLs:
1. ⏳ Eliminar `scraper_urls` de Settings
2. ⏳ Eliminar `epg_sources` de Settings
3. ⏳ Crear API para gestionar ScraperURL (tabla ya existe)
4. ⏳ Crear API para gestionar EPGSource (tabla ya existe)
5. ⏳ Modificar servicios para leer de las tablas

### Parte 3: Documentación
1. ⏳ Actualizar SETTINGS-DINAMICOS.md
2. ⏳ Actualizar API-REFERENCE.md
3. ⏳ Actualizar MEJORAS-IMPLEMENTADAS.md
4. ⏳ Crear guía de uso para gestión de URLs

---

## ✅ FASE 1: APIs para Gestión de URLs - COMPLETADA

### Estado: ✅ COMPLETADA
### Fecha de completación: 24 de enero de 2026

### Objetivo
Crear endpoints profesionales para gestionar fuentes M3U y EPG individualmente.

### Archivos a Crear

#### 1.1. `app/api/scraper.py` - API de Scraper URLs
```python
# Endpoints:
GET    /api/scraper/sources          # Listar todas las fuentes
POST   /api/scraper/sources          # Agregar nueva fuente
PUT    /api/scraper/sources/{id}     # Actualizar fuente
DELETE /api/scraper/sources/{id}     # Eliminar fuente
```

**Funcionalidades**:
- Listar todas las URLs de scraper con su estado
- Agregar nuevas URLs individualmente
- Habilitar/deshabilitar URLs sin borrarlas
- Validar que no haya URLs duplicadas
- Mostrar estadísticas (última vez scrapeada, canales encontrados)

#### 1.2. `app/api/epg.py` - API de EPG Sources
```python
# Endpoints:
GET    /api/epg/sources              # Listar todas las fuentes
POST   /api/epg/sources              # Agregar nueva fuente
PUT    /api/epg/sources/{id}         # Actualizar fuente
DELETE /api/epg/sources/{id}         # Eliminar fuente
```

**Funcionalidades**:
- Listar todas las URLs de EPG con su estado
- Agregar nuevas URLs individualmente
- Habilitar/deshabilitar URLs sin borrarlas
- Validar que no haya URLs duplicadas
- Mostrar estadísticas (última actualización, programas encontrados)

### Archivos a Modificar

#### 1.3. `main.py`
```python
# Agregar imports:
from app.api import scraper
from app.api import epg

# Registrar routers:
app.include_router(scraper.router, prefix="/api", tags=["Scraper"])
app.include_router(epg.router, prefix="/api", tags=["EPG"])
```

### Pruebas

```bash
# Listar fuentes actuales
curl http://localhost:6880/api/scraper/sources -u "admin:Admin2024!Secure"
curl http://localhost:6880/api/epg/sources -u "admin:Admin2024!Secure"

# Agregar nueva fuente M3U
curl -X POST http://localhost:6880/api/scraper/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://nueva-fuente.com/lista.m3u","is_enabled":true}'

# Agregar nueva fuente EPG
curl -X POST http://localhost:6880/api/epg/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://nueva-fuente.com/epg.xml","is_enabled":true}'

# Deshabilitar una fuente sin borrarla
curl -X PUT http://localhost:6880/api/scraper/sources/1 \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled":false}'

# Eliminar una fuente
curl -X DELETE http://localhost:6880/api/scraper/sources/2 \
  -u "admin:Admin2024!Secure"
```

---

## ✅ FASE 2: Eliminar Settings Obsoletos - COMPLETADA

### Estado: ✅ COMPLETADA
### Fecha de completación: 24 de enero de 2026

### Objetivo
Eliminar `scraper_urls` y `epg_sources` de Settings ya que ahora se gestionan con las tablas.

### Archivos a Modificar

#### 2.1. `main.py` - Inicialización de Settings
```python
# ELIMINAR estas líneas:
Setting(key="scraper_urls", value=",".join(config.get_scraper_urls_list()), ...),
Setting(key="epg_sources", value=",".join(config.get_epg_sources_list()), ...),

# Resultado: 22 settings en lugar de 24
```

#### 2.2. Base de datos existente
```bash
# Si ya tienes settings creados, eliminarlos:
curl -X DELETE http://localhost:6880/api/settings/scraper_urls -u "admin:Admin2024!Secure"
curl -X DELETE http://localhost:6880/api/settings/epg_sources -u "admin:Admin2024!Secure"
```

### Resultado
- Settings pasa de 24 a 22 entradas
- Las URLs se gestionan exclusivamente desde las tablas ScraperURL y EPGSource

---

## ✅ FASE 3: Hacer Dinámicos los 6 Settings Restantes - COMPLETADA

### Estado: ✅ COMPLETADA
### Fecha de completación: 24 de enero de 2026

### Objetivo
Modificar el código para que estos 6 settings se lean dinámicamente.

### 3.1. `epg_cache_file` - Dinámico

**Archivo**: `app/services/epg_service.py`

**Cambio**:
```python
# ANTES (línea ~156):
cache_file = self.config.epg_cache_file

# DESPUÉS:
from app.config import get_config
config = get_config()
cache_file = config.epg_cache_file
```

**Dónde aplicar**: En los métodos que guardan/cargan el cache EPG.

### 3.2. `acestream_timeout` - Dinámico

**Archivo**: `app/services/aceproxy_service.py`

**Cambio**:
```python
# ANTES (línea ~65):
self.timeout = timeout  # Fijado al inicio

# DESPUÉS:
# Leer dinámicamente en cada petición
from app.config import get_config
config = get_config()
timeout = config.acestream_timeout
```

**Dónde aplicar**: En el método `check_stream_availability()` y otros que usan timeout.

### 3.3. `acestream_chunk_size` - Dinámico

**Archivo**: `app/services/aiohttp_streaming_server.py`

**Cambio**:
```python
# Leer dinámicamente al crear nuevos streams
from app.config import get_config
config = get_config()
chunk_size = config.acestream_chunk_size
```

**Nota**: Los streams existentes mantienen su chunk_size, solo los nuevos usan el valor actualizado.

### 3.4. `acestream_empty_timeout` - Dinámico

**Archivo**: `app/services/aiohttp_streaming_server.py`

**Cambio**: Similar a chunk_size, leer dinámicamente.

### 3.5. `acestream_no_response_timeout` - Dinámico

**Archivo**: `app/services/aiohttp_streaming_server.py`

**Cambio**: Similar a chunk_size, leer dinámicamente.

### 3.6. `access_token_expire_minutes` - Dinámico

**Archivo**: `app/utils/auth.py` (si existe generación de tokens)

**Cambio**:
```python
# Leer dinámicamente al generar tokens
from app.config import get_config
config = get_config()
expire_minutes = config.access_token_expire_minutes
```

---

## ✅ FASE 4: Modificar Servicios para Leer de Tablas - COMPLETADA

### Estado: ✅ COMPLETADA
### Fecha de completación: 24 de enero de 2026

### Objetivo
Hacer que los servicios lean las URLs desde las tablas en lugar de Settings.

### 4.1. Scraper Service

**Archivo**: `app/services/scraper_service.py`

**Método**: `scrape_m3u_sources()`

**Cambio**:
```python
# ANTES:
# Lee de config (que lee de Settings o .env)
scraper_urls = config.get_scraper_urls_list()

# DESPUÉS:
# Lee directamente de la tabla ScraperURL
from app.models import ScraperURL
scraper_urls_objs = db.query(ScraperURL).filter(ScraperURL.is_enabled == True).all()
scraper_urls = [url.url for url in scraper_urls_objs]
```

### 4.2. EPG Service

**Archivo**: `app/services/epg_service.py`

**Método**: `auto_update_loop()`

**Cambio**:
```python
# ANTES:
xmltv_sources = self.config.get_epg_sources_list()

# DESPUÉS:
from app.models import EPGSource
epg_sources_objs = self.db.query(EPGSource).filter(EPGSource.is_enabled == True).all()
xmltv_sources = [source.url for source in epg_sources_objs]
```

---

## 📦 FASE 5: Documentación

### 5.1. Actualizar `SETTINGS-DINAMICOS.md`

Agregar secciones:
- Lista completa de los 9 settings dinámicos
- Lista de los 13 settings que requieren restart
- Guía de uso de las nuevas APIs de URLs
- Ejemplos de uso completos

### 5.2. Actualizar `API-REFERENCE.md`

Agregar documentación de:
- `GET /api/scraper/sources`
- `POST /api/scraper/sources`
- `PUT /api/scraper/sources/{id}`
- `DELETE /api/scraper/sources/{id}`
- `GET /api/epg/sources`
- `POST /api/epg/sources`
- `PUT /api/epg/sources/{id}`
- `DELETE /api/epg/sources/{id}`

### 5.3. Actualizar `MEJORAS-IMPLEMENTADAS.md`

Documentar todos los cambios realizados.

---

## 📊 Resumen de Cambios

### Archivos Nuevos (2)
1. `app/api/scraper.py` - API de gestión de fuentes M3U
2. `app/api/epg.py` - API de gestión de fuentes EPG

### Archivos Modificados (6)
1. `main.py` - Registrar nuevos routers, eliminar 2 settings
2. `app/services/scraper_service.py` - Leer de tabla ScraperURL
3. `app/services/epg_service.py` - Leer de tabla EPGSource, epg_cache_file dinámico
4. `app/services/aceproxy_service.py` - Timeouts dinámicos
5. `app/services/aiohttp_streaming_server.py` - Chunk size y timeouts dinámicos
6. `app/utils/auth.py` - Token expire dinámico (si aplica)

### Documentación Actualizada (3)
1. `SETTINGS-DINAMICOS.md`
2. `API-REFERENCE.md`
3. `MEJORAS-IMPLEMENTADAS.md`

---

## ✅ Resultado Final

### Settings (22 total)

**Dinámicos (9)** - Se aplican sin reiniciar:
1. scraper_update_interval
2. epg_update_interval
3. server_timezone
4. epg_cache_file
5. acestream_timeout
6. acestream_chunk_size
7. acestream_empty_timeout
8. acestream_no_response_timeout
9. access_token_expire_minutes

**Requieren Restart (13)**:
1. server_host
2. server_port
3. server_debug
4. acestream_enabled
5. acestream_engine_host
6. acestream_engine_port
7. acestream_streaming_host
8. acestream_streaming_port
9. database_url
10. database_echo
11. database_pool_size
12. database_max_overflow
13. admin_username

### Gestión de URLs

**Scraper URLs**:
- Gestión individual desde `/api/scraper/sources`
- Agregar/eliminar/habilitar/deshabilitar URLs
- Sin límite de URLs
- Estadísticas por URL

**EPG Sources**:
- Gestión individual desde `/api/epg/sources`
- Agregar/eliminar/habilitar/deshabilitar URLs
- Sin límite de URLs
- Estadísticas por URL

---

## 🚀 Orden de Implementación

1. ✅ **FASE 1**: Crear APIs de gestión de URLs (scraper.py, epg.py) - COMPLETADA
2. ✅ **FASE 2**: Eliminar settings obsoletos (scraper_urls, epg_sources) - COMPLETADA
3. ✅ **FASE 3**: Hacer dinámicos los 6 settings restantes - COMPLETADA
4. ✅ **FASE 4**: Modificar servicios para leer de tablas - COMPLETADA
5. ✅ **FASE 5**: Actualizar documentación completa - COMPLETADA
6. ✅ **FASE 6**: Compilar, desplegar y probar - COMPLETADA
7. ✅ **FASE 7**: Commit y push - COMPLETADA

---

**Fecha de creación**: 24 de enero de 2026
**Fecha de completación**: 24 de enero de 2026
**Estado**: ✅ IMPLEMENTACIÓN COMPLETADA AL 100%

**Commit**: `c7a2be2` - "Settings Dinámicos Completos y Gestión Profesional de URLs"
