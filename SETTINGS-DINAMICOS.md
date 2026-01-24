# Settings Dinámicos - Configuración en Tiempo Real

## 🎯 Objetivo

Permitir cambiar la configuración del sistema **sin reiniciar el servidor**, aplicando los cambios inmediatamente cuando sea técnicamente posible.

## ✅ Settings Totales: 22

- **9 Dinámicos** - Se aplican sin reiniciar
- **13 Requieren Restart** - Necesitan reinicio del servidor

---

## ✅ Settings Dinámicos (9)

Estos valores se aplican **sin reiniciar el servidor**:

### 1. Scraper Configuration
- **`scraper_update_interval`** - Intervalo de actualización del scraper (segundos)
  - Se lee en cada iteración del loop
  - Cambios se aplican en el siguiente ciclo (máximo 60 segundos)
  - Ejemplo: Cambiar de 24h a 12h sin reiniciar

### 2. EPG Configuration
- **`epg_update_interval`** - Intervalo de actualización EPG (segundos)
  - Se lee en cada iteración del loop
  - Cambios se aplican en el siguiente ciclo
- **`epg_cache_file`** - Ruta del archivo de cache EPG
  - ⚠️ **NOTA**: Setting legacy, no se usa actualmente
  - El EPG se genera dinámicamente, no se guarda en archivo
  - Puede eliminarse en futuras versiones
- **`server_timezone`** - Zona horaria del servidor
  - **FASE 8**: Ahora completamente dinámico en todos los usos
  - Se lee al generar XML EPG (epg_service.py)
  - Se lee en API Xtream (xtream.py)
  - Se lee en Dashboard (dashboard.py)
  - Cambios se aplican inmediatamente en la próxima generación

### 3. AceStream Configuration (Dinámicos)
- **`acestream_timeout`** - Timeout de conexión AceStream (segundos)
  - Se lee al verificar disponibilidad de streams
  - Cambios se aplican en la próxima verificación
- **`acestream_chunk_size`** - Tamaño de chunk para streaming (bytes)
  - Se lee al iniciar nuevos streams
  - Streams existentes mantienen su chunk_size
  - Nuevos streams usan el valor actualizado
- **`acestream_empty_timeout`** - Timeout sin datos (segundos)
  - Se lee al iniciar nuevos streams
  - Cambios se aplican en nuevos streams
- **`acestream_no_response_timeout`** - Timeout sin respuesta (segundos)
  - Se lee al obtener info de streams
  - Cambios se aplican inmediatamente

### 4. Security Configuration
- **`access_token_expire_minutes`** - Tiempo de expiración de tokens (minutos)
  - Se lee al generar nuevos tokens
  - Tokens existentes mantienen su expiración original
  - Nuevos tokens usan el valor actualizado

---

## ⚠️ Settings que Requieren Restart (13)

Estos valores se leen **solo al iniciar** los servicios y requieren reinicio completo:

### Server Configuration
- `server_host` - Host del servidor (0.0.0.0 = todas las interfaces)
- `server_port` - Puerto del servidor web
- `server_debug` - Modo debug (true/false)
  - **FASE 8**: Ahora controla el nivel de logging completo
  - `false` → Logs en nivel INFO (producción)
  - `true` → Logs en nivel DEBUG (desarrollo)
  - Controla: Auto-reload + Nivel de logging de aplicación + Nivel de logging de Uvicorn

### AceStream Engine Configuration
- `acestream_enabled` - Habilitar AceStream Engine (true/false)
- `acestream_engine_host` - Host del AceStream Engine
- `acestream_engine_port` - Puerto del AceStream Engine
- `acestream_streaming_host` - Host del servidor de streaming interno
- `acestream_streaming_port` - Puerto del servidor de streaming interno

### Database Configuration
- `database_url` - URL de conexión a la base de datos
- `database_echo` - Mostrar queries SQL en logs (true/false)
- `database_pool_size` - Tamaño del pool de conexiones
- `database_max_overflow` - Máximo de conexiones adicionales

### Admin Configuration
- `admin_username` - Nombre de usuario del administrador (ReadOnly)

**Para estos valores**: Cambiar + `docker-compose restart`

---

## 🗂️ Gestión de URLs (Profesional)

### ❌ Eliminados de Settings
- `scraper_urls` - Ahora se gestionan con tabla ScraperURL
- `epg_sources` - Ahora se gestionan con tabla EPGSource

### ✅ Nuevas APIs de Gestión

#### Scraper URLs (Fuentes M3U)

**Listar fuentes**:
```bash
curl http://localhost:6880/api/scraper/sources -u "admin:Admin2024!Secure"
```

**Agregar nueva fuente**:
```bash
curl -X POST http://localhost:6880/api/scraper/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://nueva-fuente.com/lista.m3u","is_enabled":true}'
```

**Deshabilitar fuente (sin borrarla)**:
```bash
curl -X PUT http://localhost:6880/api/scraper/sources/1 \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled":false}'
```

**Eliminar fuente**:
```bash
curl -X DELETE http://localhost:6880/api/scraper/sources/1 \
  -u "admin:Admin2024!Secure"
```

#### EPG Sources (Fuentes XMLTV)

**Listar fuentes**:
```bash
curl http://localhost:6880/api/epg/sources -u "admin:Admin2024!Secure"
```

**Agregar nueva fuente**:
```bash
curl -X POST http://localhost:6880/api/epg/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://nueva-fuente.com/epg.xml","is_enabled":true}'
```

**Deshabilitar fuente**:
```bash
curl -X PUT http://localhost:6880/api/epg/sources/1 \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"is_enabled":false}'
```

**Eliminar fuente**:
```bash
curl -X DELETE http://localhost:6880/api/epg/sources/1 \
  -u "admin:Admin2024!Secure"
```

### 🎯 Ventajas de la Gestión por Tablas

✅ **Sin límite de URLs** - Agrega tantas como necesites
✅ **Gestión individual** - Habilita/deshabilita sin borrar
✅ **Estadísticas por URL** - Última actualización, canales/programas encontrados
✅ **Sin comas** - No necesitas separar URLs con comas
✅ **Más profesional** - API REST completa
✅ **Sin reinicio** - Los servicios leen de las tablas dinámicamente

---

## 🔄 Cómo Usar Settings Dinámicos

### Método 1: API + Reload (Recomendado)

**Paso 1**: Cambiar el setting
```bash
curl -X PUT http://localhost:6880/api/settings/scraper_update_interval \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"value":"43200"}'
```

**Paso 2**: Recargar configuración
```bash
curl -X POST http://localhost:6880/api/settings/reload \
  -u "admin:Admin2024!Secure"
```

**Resultado**: El cambio se aplica **inmediatamente** sin reiniciar.

### Método 2: Desde el Panel Web

1. Ir a **Settings** en el dashboard
2. Buscar el setting que quieres cambiar
3. Hacer clic en **Edit**
4. Cambiar el valor
5. Guardar
6. Hacer clic en **Reload Configuration**

---

## 📊 Comparación de Métodos

| Setting | Método | Tiempo de Aplicación | Afecta Streams Activos |
|---------|--------|---------------------|------------------------|
| `scraper_update_interval` | API + Reload | <60 segundos | No |
| `epg_update_interval` | API + Reload | Inmediato | No |
| `server_timezone` | API + Reload | Inmediato | No |
| `epg_cache_file` | API + Reload | Próxima operación | No |
| `acestream_timeout` | API + Reload | Próxima verificación | No |
| `acestream_chunk_size` | API + Reload | Solo nuevos streams | No |
| `acestream_empty_timeout` | API + Reload | Solo nuevos streams | No |
| `acestream_no_response_timeout` | API + Reload | Inmediato | No |
| `access_token_expire_minutes` | API + Reload | Solo nuevos tokens | No |
| `server_port` | Restart | ~15 segundos | Sí |
| `acestream_engine_host` | Restart | ~15 segundos | Sí |

---

## 🚀 Ejemplos Completos

### Ejemplo 1: Cambiar intervalo de scraper de 24h a 12h

```bash
# 1. Ver valor actual
curl http://localhost:6880/api/settings -u "admin:Admin2024!Secure" | grep scraper_update_interval
# Resultado: "value":"86400" (24 horas)

# 2. Cambiar a 12 horas (43200 segundos)
curl -X PUT http://localhost:6880/api/settings/scraper_update_interval \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"value":"43200"}'

# 3. Recargar configuración
curl -X POST http://localhost:6880/api/settings/reload \
  -u "admin:Admin2024!Secure"

# 4. Verificar en logs
docker-compose logs unified-acestream --tail 20
# Verás: "Scraper interval updated: 86400s → 43200s"
```

### Ejemplo 2: Agregar múltiples fuentes M3U

```bash
# Agregar primera fuente
curl -X POST http://localhost:6880/api/scraper/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://fuente1.com/lista.m3u","is_enabled":true}'

# Agregar segunda fuente
curl -X POST http://localhost:6880/api/scraper/sources \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://fuente2.com/canales.m3u","is_enabled":true}'

# Listar todas las fuentes
curl http://localhost:6880/api/scraper/sources -u "admin:Admin2024!Secure"

# Resultado: Array con todas las fuentes, sus estadísticas y estado
```

### Ejemplo 3: Cambiar chunk size para nuevos streams

```bash
# Cambiar de 8KB a 16KB
curl -X PUT http://localhost:6880/api/settings/acestream_chunk_size \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"value":"16384"}'

# Recargar
curl -X POST http://localhost:6880/api/settings/reload \
  -u "admin:Admin2024!Secure"

# Los streams activos mantienen 8KB
# Los nuevos streams usarán 16KB
```

---

## 🎯 Beneficios

✅ **Sin downtime** - No necesitas reiniciar el servidor para la mayoría de cambios
✅ **Cambios inmediatos** - Se aplican en segundos, no minutos
✅ **Fácil de usar** - API simple o panel web
✅ **Seguro** - Solo valores seguros se pueden cambiar dinámicamente
✅ **Logging** - Todos los cambios se registran en logs
✅ **Gestión profesional** - URLs individuales con estadísticas
✅ **Sin límites** - Agrega tantas fuentes como necesites

---

## ⚙️ Implementación Técnica

### Cómo Funciona

1. **Config.reload()** - Recarga valores desde DB
2. **Servicios leen config** - En cada iteración del loop o al iniciar operaciones
3. **Detectan cambios** - Comparan valor actual vs anterior
4. **Aplican cambios** - Actualizan variables internas
5. **Logging** - Registran el cambio

### Código Ejemplo (Scraper Service)

```python
async def auto_scrape_loop(self):
    while self.running:
        # Leer config dinámicamente
        config = get_config()
        current_interval = config.scraper_update_interval
        
        # Detectar cambio
        if current_interval != self.update_interval:
            logger.info(f"Interval updated: {self.update_interval}s → {current_interval}s")
            self.update_interval = current_interval
        
        # Usar nuevo valor
        if time.time() - self.last_update >= self.update_interval:
            await self.scrape_m3u_sources()
```

### Código Ejemplo (AceStream Streaming)

```python
async def _fetch_acestream(self, ongoing: OngoingStream):
    # Leer settings dinámicamente
    config = get_config()
    chunk_size = config.acestream_chunk_size
    empty_timeout = config.acestream_empty_timeout
    
    # Usar valores actualizados
    timeout = aiohttp.ClientTimeout(sock_read=empty_timeout)
    async for chunk in response.content.iter_chunked(chunk_size):
        # Procesar chunk...
```

---

## 📝 Notas Importantes

### Settings Dinámicos
- Los cambios se aplican **sin afectar operaciones en curso**
- Streams activos mantienen su configuración original
- Nuevos streams/operaciones usan los valores actualizados
- No hay riesgo de interrumpir el servicio

### Settings que Requieren Restart
- Cambiar estos valores requiere `docker-compose restart`
- El restart tarda ~15 segundos
- Todos los streams activos se interrumpen
- Úsalos solo cuando sea necesario

### Gestión de URLs
- Las URLs se leen de las tablas en cada ciclo de actualización
- Agregar/eliminar URLs no requiere reinicio
- Los servicios detectan cambios automáticamente
- Las estadísticas se actualizan en cada scraping/actualización

---

**Última actualización**: 24 de enero de 2026
**Versión**: 2.1 - FASE 8: Auditoría completa y correcciones

## 📋 Historial de Cambios

### Versión 2.1 (24 de enero de 2026) - FASE 8
- ✅ Auditoría completa de implementación de todos los settings
- ✅ Corrección de `server_debug`: Ahora controla nivel de logging completo
- ✅ Corrección de `server_timezone`: Completamente dinámico en todos los usos
- ✅ Verificación de todos los settings: 95.5% implementación real (21/22)
- ✅ Identificación de `epg_cache_file` como setting legacy no usado

### Versión 2.0 (24 de enero de 2026)
- ✅ Gestión profesional de URLs con tablas ScraperURL y EPGSource
- ✅ APIs REST completas para gestión de fuentes
- ✅ Eliminación de `scraper_urls` y `epg_sources` de Settings
- ✅ Sistema de colores en panel web (verde/amarillo/gris)

### Versión 1.0 (24 de enero de 2026)
- ✅ Implementación inicial de settings dinámicos
- ✅ 9 settings dinámicos funcionando
- ✅ 13 settings que requieren restart
