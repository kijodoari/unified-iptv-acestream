# Settings Dinámicos - Configuración en Tiempo Real

## 🎯 Objetivo

Permitir cambiar la configuración del sistema **sin reiniciar el servidor**, aplicando los cambios inmediatamente.

## ✅ Valores que se Aplican Dinámicamente

### 1. Scraper Configuration
- **`scraper_update_interval`** - Intervalo de actualización del scraper (segundos)
  - Se lee en cada iteración del loop
  - Cambios se aplican en el siguiente ciclo (máximo 60 segundos)

### 2. EPG Configuration
- **`epg_update_interval`** - Intervalo de actualización EPG (segundos)
  - Se lee en cada iteración del loop
  - Cambios se aplican en el siguiente ciclo
- **`server_timezone`** - Zona horaria del servidor
  - Se lee al generar XML EPG
  - Cambios se aplican inmediatamente en la próxima generación

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
6. Hacer clic en **Reload Configuration** (botón nuevo)

## ⚠️ Valores que Requieren Reinicio

Estos valores se leen **solo al iniciar** los servicios y requieren reinicio completo:

### AceStream Configuration
- `acestream_enabled` - Habilitar/deshabilitar AceStream
- `acestream_engine_host` - Host del AceStream Engine
- `acestream_engine_port` - Puerto del AceStream Engine
- `acestream_timeout` - Timeout de conexión
- `acestream_streaming_host` - Host del servidor de streaming
- `acestream_streaming_port` - Puerto del servidor de streaming
- `acestream_chunk_size` - Tamaño de chunk
- `acestream_empty_timeout` - Timeout sin datos
- `acestream_no_response_timeout` - Timeout sin respuesta

### Server Configuration
- `server_host` - Host del servidor
- `server_port` - Puerto del servidor
- `server_debug` - Modo debug

### Database Configuration
- `database_url` - URL de la base de datos
- `database_echo` - Mostrar queries SQL
- `database_pool_size` - Tamaño del pool
- `database_max_overflow` - Máximo de conexiones

### Scraper URLs y EPG Sources
- `scraper_urls` - URLs de fuentes M3U
- `epg_sources` - URLs de fuentes EPG XMLTV

**Para estos valores**: Cambiar + `docker-compose restart`

## 📊 Comparación

| Valor | Método | Tiempo de Aplicación |
|-------|--------|---------------------|
| `scraper_update_interval` | API + Reload | <60 segundos |
| `epg_update_interval` | API + Reload | Inmediato |
| `server_timezone` | API + Reload | Inmediato |
| `acestream_timeout` | Restart | ~15 segundos |
| `server_port` | Restart | ~15 segundos |
| `scraper_urls` | Restart | ~15 segundos |

## 🚀 Ejemplo Completo

### Cambiar intervalo de scraper de 24h a 12h sin reiniciar:

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

## 🎯 Beneficios

✅ **Sin downtime** - No necesitas reiniciar el servidor
✅ **Cambios inmediatos** - Se aplican en segundos, no minutos
✅ **Fácil de usar** - API simple o panel web
✅ **Seguro** - Solo valores seguros se pueden cambiar dinámicamente
✅ **Logging** - Todos los cambios se registran en logs

## ⚙️ Implementación Técnica

### Cómo Funciona

1. **Config.reload()** - Recarga valores desde DB
2. **Servicios leen config** - En cada iteración del loop
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

## 🔮 Futuras Mejoras

- [ ] Agregar más valores dinámicos (acestream_timeout, etc.)
- [ ] Sistema de notificaciones cuando cambia un setting
- [ ] Validación de valores antes de aplicar
- [ ] Rollback automático si un valor causa error
- [ ] Hot reload completo sin necesidad de endpoint

---

**Última actualización**: 24 de enero de 2026
