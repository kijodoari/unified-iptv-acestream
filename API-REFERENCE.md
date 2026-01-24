# Referencia Completa de APIs
## Unified IPTV AceStream Platform

**Última actualización**: 24 de enero de 2026  
**Versión**: 1.0.0

---

## 📋 Índice

1. [API Principal (Root)](#api-principal-root)
2. [API de Dashboard](#api-de-dashboard)
3. [API de Gestión de Canales](#api-de-gestión-de-canales)
4. [API de Gestión de Usuarios](#api-de-gestión-de-usuarios)
5. [API de Configuración (Settings)](#api-de-configuración-settings)
6. [API Xtream Codes](#api-xtream-codes)
7. [API de EPG](#api-de-epg)
8. [API de AceProxy](#api-de-aceproxy)
9. [API de Scraper](#api-de-scraper)
10. [API de Logs](#api-de-logs)
11. [API de Búsqueda AceStream](#api-de-búsqueda-acestream)

---

## API Principal (Root)

### GET /

**Descripción**: Información general de la API

**Autenticación**: No requerida

**Respuesta**:
```json
{
  "name": "Unified IPTV AceStream Platform",
  "version": "1.0.0",
  "endpoints": {
    "xtream_api": "http://localhost:6880/player_api.php",
    "m3u_playlist": "http://localhost:6880/get.php",
    "epg": "http://localhost:6880/xmltv.php",
    "aceproxy": "http://localhost:6880/ace/getstream",
    "health": "/health",
    "docs": "/docs"
  }
}
```

### GET /health

**Descripción**: Health check del sistema

**Autenticación**: No requerida

**Respuesta**:
```json
{
  "status": "healthy",
  "services": {
    "aceproxy": true,
    "scraper": true,
    "epg": true
  },
  "aceproxy_streams": 0
}
```

---

## API de Dashboard

### GET /

**Descripción**: Página principal del dashboard

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

### GET /channels

**Descripción**: Página de gestión de canales

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

### GET /users

**Descripción**: Página de gestión de usuarios

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

### GET /scraper

**Descripción**: Página de configuración del scraper

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

### GET /epg

**Descripción**: Página de gestión de EPG

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

### GET /settings

**Descripción**: Página de configuración

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**: HTML

---

## API de Gestión de Canales

### GET /api/dashboard/stats

**Descripción**: Estadísticas del dashboard

**Autenticación**: No requerida

**Respuesta**:
```json
{
  "total_channels": 100,
  "online_channels": 85,
  "active_channels": 95,
  "total_users": 5,
  "active_users": 4,
  "total_categories": 10,
  "scraper_urls": 2,
  "enabled_scraper_urls": 2,
  "epg_sources": 1,
  "active_streams": 3,
  "active_connections": 5,
  "acestream_engine": {
    "status": "online",
    "available": true
  }
}
```

### GET /api/channels

**Descripción**: Lista de canales

**Parámetros**:
- `limit` (int, opcional): Número máximo de canales (default: 100)
- `offset` (int, opcional): Offset para paginación (default: 0)

**Respuesta**:
```json
[
  {
    "id": 1,
    "name": "Canal 1",
    "acestream_id": "abc123...",
    "category": "Deportes",
    "logo_url": "http://...",
    "is_online": true,
    "is_active": true,
    "created_at": "2026-01-24T12:00:00"
  }
]
```

### GET /api/channels/{channel_id}

**Descripción**: Detalles de un canal específico

**Parámetros**:
- `channel_id` (int, requerido): ID del canal

**Respuesta**:
```json
{
  "id": 1,
  "name": "Canal 1",
  "acestream_id": "abc123...",
  "stream_url": "http://...",
  "category": "Deportes",
  "category_id": 1,
  "logo_url": "http://...",
  "epg_id": "canal1.tv",
  "language": "es",
  "country": "ES",
  "description": "Descripción del canal",
  "is_online": true,
  "is_active": true,
  "created_at": "2026-01-24T12:00:00",
  "updated_at": "2026-01-24T12:00:00"
}
```

### POST /api/channels

**Descripción**: Crear un nuevo canal

**Body**:
```json
{
  "name": "Nuevo Canal",
  "acestream_id": "abc123...",
  "stream_url": "http://...",
  "category": "Deportes",
  "logo_url": "http://...",
  "epg_id": "canal.tv",
  "language": "es",
  "country": "ES",
  "description": "Descripción"
}
```

**Respuesta**:
```json
{
  "id": 101,
  "name": "Nuevo Canal",
  "message": "Channel created successfully"
}
```

### PUT /api/channels/{channel_id}

**Descripción**: Actualizar un canal existente

**Parámetros**:
- `channel_id` (int, requerido): ID del canal

**Body**:
```json
{
  "name": "Canal Actualizado",
  "category": "Entretenimiento",
  "logo_url": "http://...",
  "epg_id": "canal.tv",
  "is_active": true
}
```

**Respuesta**:
```json
{
  "id": 1,
  "name": "Canal Actualizado",
  "message": "Channel updated successfully"
}
```

### DELETE /api/channels/{channel_id}

**Descripción**: Eliminar un canal

**Parámetros**:
- `channel_id` (int, requerido): ID del canal

**Respuesta**:
```json
{
  "message": "Channel deleted successfully"
}
```

---

## API Xtream Codes

### GET /player_api.php

**Descripción**: API principal de Xtream Codes

**Parámetros**:
- `username` (string, requerido): Nombre de usuario
- `password` (string, requerido): Contraseña
- `action` (string, opcional): Acción a realizar

**Acciones disponibles**:

#### Sin action (Información de usuario y servidor)

**Ejemplo**: `/player_api.php?username=admin&password=pass`

**Respuesta**:
```json
{
  "user_info": {
    "username": "admin",
    "password": "pass",
    "message": "",
    "auth": 1,
    "status": "Active",
    "is_trial": 0,
    "active_cons": 0,
    "created_at": 1706097600,
    "max_connections": 1,
    "allowed_output_formats": ["m3u8", "ts"]
  },
  "server_info": {
    "url": "localhost",
    "port": "6880",
    "https_port": "6880",
    "server_protocol": "http",
    "rtmp_port": "0",
    "timezone": "GMT",
    "timestamp_now": 1706097600,
    "time_now": "2026-01-24 12:00:00"
  }
}
```

#### action=get_live_categories

**Ejemplo**: `/player_api.php?username=admin&password=pass&action=get_live_categories`

**Respuesta**:
```json
[
  {
    "category_id": "1",
    "category_name": "Deportes",
    "parent_id": 0
  }
]
```

#### action=get_live_streams

**Ejemplo**: `/player_api.php?username=admin&password=pass&action=get_live_streams`

**Parámetros opcionales**:
- `category_id` (string): Filtrar por categoría

**Respuesta**:
```json
[
  {
    "num": 1,
    "name": "Canal 1",
    "stream_type": "live",
    "stream_id": 1,
    "stream_icon": "http://...",
    "epg_channel_id": "canal1.tv",
    "added": "1706097600",
    "is_adult": "0",
    "category_id": "1",
    "category_ids": [1],
    "custom_sid": null,
    "tv_archive": 0,
    "direct_source": "",
    "tv_archive_duration": 0
  }
]
```

#### action=get_short_epg

**Ejemplo**: `/player_api.php?username=admin&password=pass&action=get_short_epg&stream_id=1&limit=4`

**Parámetros**:
- `stream_id` (int, requerido): ID del canal
- `limit` (int, opcional): Número de programas (default: 4)

**Respuesta**:
```json
{
  "epg_listings": [
    {
      "id": "1",
      "epg_id": "canal1.tv",
      "title": "Programa 1",
      "lang": "",
      "start": "2026-01-24 12:00:00",
      "end": "2026-01-24 13:00:00",
      "description": "Descripción del programa",
      "channel_id": "canal1.tv",
      "start_timestamp": "1706097600",
      "stop_timestamp": "1706101200",
      "has_archive": 0
    }
  ]
}
```

#### action=get_simple_data_table

**Ejemplo**: `/player_api.php?username=admin&password=pass&action=get_simple_data_table&stream_id=1`

**Parámetros**:
- `stream_id` (int, requerido): ID del canal

**Respuesta**: Similar a get_short_epg

### GET /panel_api.php

**Descripción**: API de panel (compatible con Xtream)

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)

**Respuesta**: Similar a player_api.php sin action

### GET /live/{username}/{password}/{stream_id}
### GET /live/{username}/{password}/{stream_id}.{extension}

**Descripción**: Stream de canal en vivo

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)
- `stream_id` (int, requerido)
- `extension` (string, opcional): ts, m3u8 (default: ts)

**Respuesta**: Stream de video (video/mp2t)

### GET /{username}/{password}/{stream_id}
### GET /{username}/{password}/{stream_id}.{extension}

**Descripción**: Stream de canal (ruta alternativa)

**Parámetros**: Igual que /live/

**Respuesta**: Stream de video

### GET /get.php

**Descripción**: Obtener playlist M3U

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)
- `type` (string, opcional): m3u_plus (default)
- `output` (string, opcional): ts, m3u8 (default: ts)

**Respuesta**: Playlist M3U (audio/x-mpegurl)

```
#EXTM3U url-tvg="http://localhost:6880/xmltv.php?username=admin&password=pass"
#EXTINF:-1 tvg-logo="http://..." tvg-id="canal1.tv" group-title="Deportes",Canal 1
http://localhost:6880/live/admin/pass/1.ts
```

### GET /xmltv.php

**Descripción**: Obtener EPG en formato XMLTV

**Parámetros**:
- `username` (string, opcional)
- `password` (string, opcional)

**Respuesta**: XML (application/xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="canal1.tv">
    <display-name>Canal 1</display-name>
  </channel>
  <programme start="20260124120000" stop="20260124130000" channel="canal1.tv">
    <title>Programa 1</title>
    <desc>Descripción</desc>
  </programme>
</tv>
```

---

## API de EPG

### POST /epg/update

**Descripción**: Actualizar EPG manualmente

**Autenticación**: Requiere usuario admin

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)

**Respuesta**:
```json
{
  "success": true,
  "method": "xmltv",
  "programmes_updated": 3419,
  "message": "EPG updated successfully using XMLTV method"
}
```

### GET /epg/status

**Descripción**: Estado y estadísticas del EPG

**Autenticación**: Requiere autenticación

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)

**Respuesta**:
```json
{
  "total_channels": 100,
  "channels_with_epg_id": 72,
  "total_programs": 3419,
  "current_programs": 50,
  "future_programs": 3369,
  "xmltv_sources": ["https://..."],
  "xmltv_sources_count": 1,
  "database_sources": [],
  "database_sources_count": 0,
  "update_interval": 86400,
  "cache_file": "data/epg.xml"
}
```

### GET /epg/channel/{channel_id}

**Descripción**: EPG de un canal específico

**Parámetros**:
- `channel_id` (int, requerido)
- `username` (string, opcional)
- `password` (string, opcional)
- `hours` (int, opcional): Horas de EPG (default: 24)

**Respuesta**:
```json
{
  "channel_id": 1,
  "channel_name": "Canal 1",
  "epg_id": "canal1.tv",
  "programs": [
    {
      "id": 1,
      "title": "Programa 1",
      "description": "Descripción",
      "start_time": "2026-01-24T12:00:00",
      "end_time": "2026-01-24T13:00:00",
      "duration_minutes": 60,
      "category": "Deportes",
      "icon_url": "http://...",
      "rating": "PG"
    }
  ],
  "total_programs": 10
}
```

### POST /epg/clean_duplicates

**Descripción**: Limpiar programas EPG duplicados

**Autenticación**: Requiere usuario admin

**Parámetros**:
- `username` (string, requerido)
- `password` (string, requerido)
- `channel_id` (int, opcional): Canal específico o todos

**Respuesta**:
```json
{
  "success": true,
  "duplicates_removed": 15,
  "message": "Successfully removed 15 duplicate programs"
}
```

---

## API de AceProxy

### GET /ace/getstream

**Descripción**: Stream de contenido AceStream

**Parámetros**:
- `id` (string): AceStream content ID
- `infohash` (string): Torrent infohash

**Nota**: Solo uno de `id` o `infohash` debe especificarse

**Respuesta**: Stream de video (video/MP2T)

### GET /ace/status

**Descripción**: Estado del proxy AceStream

**Parámetros**:
- `id` (string, opcional): ID específico
- `infohash` (string, opcional): Infohash específico

**Respuesta**:
```json
{
  "status": "active",
  "streams": 3,
  "clients": 5
}
```

### GET /api/aceproxy/streams

**Descripción**: Lista de streams activos

**Respuesta**:
```json
{
  "status": "success",
  "total_streams": 3,
  "streams": [
    {
      "stream_id": "abc123...",
      "channel_name": "Canal 1",
      "clients": [
        {
          "username": "admin",
          "ip": "192.168.1.100",
          "user_agent": "VLC/3.0",
          "connected_at": "2026-01-24T12:00:00",
          "connection_count": 1
        }
      ],
      "client_count": 1,
      "physical_connections": 1,
      "created_at": "2026-01-24T12:00:00",
      "is_active": true
    }
  ]
}
```

### GET /api/aceproxy/streams/{stream_id}

**Descripción**: Información de un stream específico

**Parámetros**:
- `stream_id` (string, requerido)

**Respuesta**:
```json
{
  "status": "success",
  "stream": {
    "stream_id": "abc123...",
    "clients": 2,
    "is_active": true
  }
}
```

### DELETE /api/aceproxy/streams/{stream_id}

**Descripción**: Cerrar un stream (no soportado en patrón pyacexy)

**Parámetros**:
- `stream_id` (string, requerido)

**Respuesta**:
```json
{
  "status": "info",
  "message": "Streams close automatically when all clients disconnect (pyacexy pattern)"
}
```

### GET /api/aceproxy/stats

**Descripción**: Estadísticas generales de AceProxy

**Respuesta**:
```json
{
  "status": "success",
  "stats": {
    "total_streams": 3,
    "total_clients": 0,
    "server_type": "aiohttp native pyacexy",
    "streaming_port": 6881
  }
}
```

---

## API de Scraper

### POST /api/scraper/trigger

**Descripción**: Ejecutar scraping manual

**Respuesta**:
```json
{
  "status": "success",
  "message": "Scraped 150 channels from 2 source(s)",
  "details": {
    "total_channels": 150,
    "sources_processed": 2,
    "results": {
      "https://source1.com/m3u": 100,
      "https://source2.com/m3u": 50
    },
    "elapsed_seconds": 5.23
  }
}
```

### POST /api/epg/update

**Descripción**: Actualizar EPG (endpoint alternativo)

**Respuesta**:
```json
{
  "status": "triggered",
  "message": "EPG update will start shortly"
}
```

### POST /api/channels/check

**Descripción**: Verificar estado de canales

**Respuesta**:
```json
{
  "status": "triggered",
  "message": "Channel check will start shortly"
}
```

---

## API de Gestión de Usuarios

### GET /api/users

**Descripción**: Lista de todos los usuarios

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true,
    "is_admin": true,
    "is_trial": false,
    "max_connections": 1,
    "expiry_date": null,
    "created_at": "2026-01-24T12:00:00",
    "last_login": "2026-01-24T13:00:00",
    "notes": null
  }
]
```

### POST /api/users

**Descripción**: Crear un nuevo usuario

**Autenticación**: HTTP Basic Auth (admin)

**Body**:
```json
{
  "username": "nuevo_usuario",
  "password": "Password123!",
  "email": "usuario@example.com",
  "is_active": true,
  "is_admin": false,
  "is_trial": false,
  "max_connections": 2,
  "expiry_date": "2026-12-31T23:59:59",
  "notes": "Usuario de prueba"
}
```

**Respuesta**:
```json
{
  "id": 5,
  "username": "nuevo_usuario",
  "message": "User created successfully"
}
```

### PUT /api/users/{user_id}

**Descripción**: Actualizar un usuario existente

**Autenticación**: HTTP Basic Auth (admin)

**Parámetros**:
- `user_id` (int, requerido): ID del usuario

**Body**:
```json
{
  "email": "nuevo_email@example.com",
  "is_active": true,
  "max_connections": 3,
  "expiry_date": "2027-01-01T00:00:00",
  "notes": "Usuario actualizado"
}
```

**Respuesta**:
```json
{
  "id": 5,
  "username": "nuevo_usuario",
  "message": "User updated successfully"
}
```

### DELETE /api/users/{user_id}

**Descripción**: Eliminar un usuario

**Autenticación**: HTTP Basic Auth (admin)

**Parámetros**:
- `user_id` (int, requerido): ID del usuario

**Respuesta**:
```json
{
  "message": "User deleted successfully"
}
```

### POST /api/users/{user_id}/reset-password

**Descripción**: Restablecer contraseña de un usuario

**Autenticación**: HTTP Basic Auth (admin)

**Parámetros**:
- `user_id` (int, requerido): ID del usuario

**Body**:
```json
{
  "new_password": "NewPassword123!"
}
```

**Respuesta**:
```json
{
  "message": "Password reset successfully"
}
```

---

## API de Configuración (Settings)

### GET /api/settings

**Descripción**: Lista de todas las configuraciones

**Autenticación**: HTTP Basic Auth (admin)

**Respuesta**:
```json
[
  {
    "id": 1,
    "key": "server_name",
    "value": "Unified IPTV Platform",
    "description": "Nombre del servidor",
    "category": "general",
    "created_at": "2026-01-24T12:00:00",
    "updated_at": "2026-01-24T12:00:00"
  }
]
```

### POST /api/settings

**Descripción**: Crear una nueva configuración

**Autenticación**: HTTP Basic Auth (admin)

**Body**:
```json
{
  "key": "nueva_config",
  "value": "valor",
  "description": "Descripción de la configuración",
  "category": "general"
}
```

**Respuesta**:
```json
{
  "id": 10,
  "key": "nueva_config",
  "message": "Setting created successfully"
}
```

### PUT /api/settings/{setting_id}

**Descripción**: Actualizar una configuración existente

**Autenticación**: HTTP Basic Auth (admin)

**Parámetros**:
- `setting_id` (int, requerido): ID de la configuración

**Body**:
```json
{
  "value": "nuevo_valor",
  "description": "Nueva descripción"
}
```

**Respuesta**:
```json
{
  "id": 10,
  "key": "nueva_config",
  "message": "Setting updated successfully"
}
```

### DELETE /api/settings/{setting_id}

**Descripción**: Eliminar una configuración

**Autenticación**: HTTP Basic Auth (admin)

**Parámetros**:
- `setting_id` (int, requerido): ID de la configuración

**Respuesta**:
```json
{
  "message": "Setting deleted successfully"
}
```

### POST /api/settings/bulk-update

**Descripción**: Actualizar múltiples configuraciones a la vez

**Autenticación**: HTTP Basic Auth (admin)

**Body**:
```json
{
  "settings": [
    {
      "key": "server_name",
      "value": "Nuevo Nombre"
    },
    {
      "key": "max_streams",
      "value": "100"
    }
  ]
}
```

**Respuesta**:
```json
{
  "message": "2 settings updated successfully",
  "updated_count": 2
}
```

### POST /api/settings/reload

**Descripción**: Recargar configuración desde la base de datos sin reiniciar el servidor

**Autenticación**: HTTP Basic Auth (admin)

**Uso**: Después de modificar settings, llama a este endpoint para aplicar los cambios dinámicamente (sin reiniciar).

**Respuesta**:
```json
{
  "status": "success",
  "message": "Configuration reloaded successfully",
  "note": "Some services may need to be restarted for changes to take full effect"
}
```

**Settings que se aplican dinámicamente** (sin reiniciar):
- `scraper_update_interval` - Intervalo de scraping (se aplica en <60s)
- `epg_update_interval` - Intervalo de EPG (se aplica inmediatamente)
- `server_timezone` - Zona horaria (se aplica al generar EPG)

**Settings que requieren restart**:
- Todos los demás (AceStream, Server, Database) requieren `docker-compose restart`

**Ejemplo de uso**:
```bash
# 1. Cambiar intervalo de scraper a 12 horas
curl -X PUT http://localhost:6880/api/settings/scraper_update_interval \
  -u "admin:Admin2024!Secure" \
  -H "Content-Type: application/json" \
  -d '{"value":"43200"}'

# 2. Recargar configuración
curl -X POST http://localhost:6880/api/settings/reload \
  -u "admin:Admin2024!Secure"

# Resultado: Cambio aplicado en menos de 60 segundos sin reiniciar
```

---

## API de Logs

### GET /api/logs/tail

**Descripción**: Obtener últimas líneas del log

**Parámetros**:
- `lines` (int, opcional): Número de líneas (default: 100)

**Respuesta**:
```json
{
  "lines": [
    "2026-01-24 12:00:00 - INFO - Server started\n",
    "2026-01-24 12:00:01 - INFO - Channel loaded\n"
  ],
  "total_lines": 1000,
  "returned_lines": 100
}
```

### GET /api/logs/download

**Descripción**: Descargar archivo de log completo

**Respuesta**: Texto plano con todo el log

### DELETE /api/logs/clear

**Descripción**: Limpiar archivo de log

**Respuesta**:
```json
{
  "message": "Log file cleared successfully"
}
```

### WS /api/logs/stream

**Descripción**: Stream de logs en tiempo real (WebSocket)

**Mensajes recibidos**:
```json
{
  "type": "logs",
  "lines": ["2026-01-24 12:00:00 - INFO - New log line\n"]
}
```

---

## API de Búsqueda AceStream

### GET /m3u

**Descripción**: Búsqueda de contenido AceStream

**Parámetros**:
- `query` (string): Término de búsqueda
- `json` (bool, opcional): Formato JSON
- `xml_epg` (bool, opcional): Formato XML EPG
- `url` (bool, opcional): Redirigir a URL

**Respuesta**: M3U, JSON o XML según parámetros

---

## 🔐 Autenticación

### HTTP Basic Authentication

Usado en:
- Dashboard web (todas las páginas)
- Algunos endpoints de administración

**Headers**:
```
Authorization: Basic base64(username:password)
```

### Xtream Codes Authentication

Usado en:
- API Xtream Codes
- Streaming de canales

**Parámetros en URL**:
```
?username=admin&password=pass
```

---

## 📊 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Parámetros inválidos |
| 401 | Unauthorized - Autenticación requerida |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |
| 503 | Service Unavailable - Servicio no disponible |

---

## 🔗 URLs Base

### Desarrollo Local
```
http://localhost:6880
```

### Producción
```
http://tu-servidor:6880
```

---

## 📝 Ejemplos de Uso

### Obtener lista de canales (cURL)

```bash
curl -X GET "http://localhost:6880/api/channels?limit=10"
```

### Crear un canal (cURL)

```bash
curl -X POST "http://localhost:6880/api/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nuevo Canal",
    "acestream_id": "abc123...",
    "category": "Deportes"
  }'
```

### Obtener playlist M3U (navegador)

```
http://localhost:6880/get.php?username=admin&password=Admin2024!Secure&type=m3u_plus
```

### Stream de canal (VLC)

```
http://localhost:6880/live/admin/Admin2024!Secure/1.ts
```

---

## 🔮 APIs Futuras (Roadmap)

### VOD (Video on Demand)
- `GET /player_api.php?action=get_vod_categories`
- `GET /player_api.php?action=get_vod_streams`
- `GET /movie/{username}/{password}/{vod_id}.{ext}`

### Series
- `GET /player_api.php?action=get_series_categories`
- `GET /player_api.php?action=get_series`
- `GET /series/{username}/{password}/{episode_id}.{ext}`

### Gestión Avanzada
- Estadísticas detalladas por usuario
- Límites de ancho de banda
- Geolocalización de conexiones

---

## 📚 Documentos Relacionados

- **[README.md](./README.md)** - Documentación principal
- **[INSTALACION-COMPLETA.md](./INSTALACION-COMPLETA.md)** - Guía de instalación
- **[ACCESO.md](./ACCESO.md)** - Guía de acceso
- **[MEJORAS-IMPLEMENTADAS.md](./MEJORAS-IMPLEMENTADAS.md)** - Registro de cambios

---

**Repositorio**: https://github.com/TokyoghoulEs/unified-iptv-acestream  
**Licencia**: MIT  
**Versión de la API**: 1.0.0


---

## API de Gestión de Fuentes Scraper

### GET /api/scraper/sources

**Descripción**: Listar todas las fuentes M3U del scraper

**Autenticación**: HTTP Basic Auth

**Respuesta**:
```json
[
  {
    "id": 1,
    "url": "https://wafy80.github.io/m3u",
    "is_enabled": true,
    "last_scraped": "2026-01-24T17:48:02.039668",
    "channels_found": 150,
    "created_at": "2026-01-24T12:11:26.995200"
  }
]
```

### POST /api/scraper/sources

**Descripción**: Agregar nueva fuente M3U

**Autenticación**: HTTP Basic Auth

**Body**:
```json
{
  "url": "https://nueva-fuente.com/lista.m3u",
  "is_enabled": true
}
```

**Respuesta**:
```json
{
  "id": 2,
  "url": "https://nueva-fuente.com/lista.m3u",
  "message": "Scraper source created successfully"
}
```

### PUT /api/scraper/sources/{source_id}

**Descripción**: Actualizar fuente M3U existente

**Autenticación**: HTTP Basic Auth

**Parámetros**:
- `source_id` (path): ID de la fuente

**Body**:
```json
{
  "url": "https://fuente-actualizada.com/lista.m3u",
  "is_enabled": false
}
```

**Respuesta**:
```json
{
  "id": 2,
  "url": "https://fuente-actualizada.com/lista.m3u",
  "message": "Scraper source updated successfully"
}
```

### DELETE /api/scraper/sources/{source_id}

**Descripción**: Eliminar fuente M3U

**Autenticación**: HTTP Basic Auth

**Parámetros**:
- `source_id` (path): ID de la fuente

**Respuesta**:
```json
{
  "message": "Scraper source deleted successfully"
}
```

---

## API de Gestión de Fuentes EPG

### GET /api/epg/sources

**Descripción**: Listar todas las fuentes EPG XMLTV

**Autenticación**: HTTP Basic Auth

**Respuesta**:
```json
[
  {
    "id": 1,
    "url": "https://wafy80.github.io/epg_light.xml",
    "is_enabled": true,
    "last_updated": "2026-01-24T17:48:02.976969",
    "programs_found": 3081,
    "created_at": "2026-01-24T12:11:27.021741"
  }
]
```

### POST /api/epg/sources

**Descripción**: Agregar nueva fuente EPG

**Autenticación**: HTTP Basic Auth

**Body**:
```json
{
  "url": "https://nueva-fuente.com/epg.xml",
  "is_enabled": true
}
```

**Respuesta**:
```json
{
  "id": 2,
  "url": "https://nueva-fuente.com/epg.xml",
  "message": "EPG source created successfully"
}
```

### PUT /api/epg/sources/{source_id}

**Descripción**: Actualizar fuente EPG existente

**Autenticación**: HTTP Basic Auth

**Parámetros**:
- `source_id` (path): ID de la fuente

**Body**:
```json
{
  "url": "https://fuente-actualizada.com/epg.xml",
  "is_enabled": false
}
```

**Respuesta**:
```json
{
  "id": 2,
  "url": "https://fuente-actualizada.com/epg.xml",
  "message": "EPG source updated successfully"
}
```

### DELETE /api/epg/sources/{source_id}

**Descripción**: Eliminar fuente EPG

**Autenticación**: HTTP Basic Auth

**Parámetros**:
- `source_id` (path): ID de la fuente

**Respuesta**:
```json
{
  "message": "EPG source deleted successfully"
}
```

---

## 📝 Notas sobre Gestión de Fuentes

### Ventajas del Nuevo Sistema

1. **Sin límite de URLs**: Agrega tantas fuentes como necesites
2. **Gestión individual**: Habilita/deshabilita sin borrar
3. **Estadísticas por fuente**: Última actualización, canales/programas encontrados
4. **Sin comas**: No necesitas separar URLs con comas
5. **API REST completa**: CRUD completo para cada fuente
6. **Sin reinicio**: Los servicios leen de las tablas dinámicamente

### Migración desde Settings

**Antes** (Settings):
```bash
# scraper_urls: "https://fuente1.com/m3u,https://fuente2.com/m3u"
# epg_sources: "https://fuente1.com/epg.xml,https://fuente2.com/epg.xml"
```

**Ahora** (Tablas):
```bash
# Agregar fuentes individualmente
POST /api/scraper/sources {"url":"https://fuente1.com/m3u"}
POST /api/scraper/sources {"url":"https://fuente2.com/m3u"}
POST /api/epg/sources {"url":"https://fuente1.com/epg.xml"}
POST /api/epg/sources {"url":"https://fuente2.com/epg.xml"}
```

### Comportamiento de los Servicios

- **Scraper Service**: Lee todas las fuentes habilitadas en cada ciclo de scraping
- **EPG Service**: Lee todas las fuentes habilitadas en cada actualización de EPG
- **Detección automática**: Los servicios detectan cambios en las tablas sin reiniciar
- **Estadísticas**: Se actualizan automáticamente después de cada scraping/actualización

---

**Última actualización**: 24 de enero de 2026  
**Versión**: 2.0 - Gestión profesional de fuentes
