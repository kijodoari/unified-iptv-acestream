# Guía de Acceso - Unified IPTV AceStream Platform

## � Credenciales de Acceso

### Dashboard Web
- **URL**: http://localhost:6880
- **Usuario**: admin
- **Contraseña**: Admin2024!Secure

El dashboard está protegido y solo es accesible desde localhost por defecto.

## 📺 Acceso a Canales IPTV

### Opción 1: Xtream Codes API (Recomendado)

Compatible con IPTV Smarters, Perfect Player, TiviMate y otros clientes IPTV.

**Configuración**:
- **URL del servidor**: http://localhost:6880
- **Usuario**: admin
- **Contraseña**: Admin2024!Secure
- **Tipo**: Xtream Codes API

### Opción 2: Playlist M3U

**URL de la playlist**:
```
http://localhost:6880/get.php?username=admin&password=Admin2024!Secure&type=m3u_plus&output=ts
```

### Opción 3: EPG (Guía Electrónica de Programación)

**URL del EPG**:
```
http://localhost:6880/xmltv.php?username=admin&password=Admin2024!Secure
```

## 🎬 Reproducción de Canales

### ⚠️ IMPORTANTE: Limitación del Navegador Web

**Los navegadores web NO pueden reproducir streams MPEG-TS en vivo directamente**. Esto es una limitación técnica de HTML5 Video, no un problema de la plataforma.

**Los streams SÍ funcionan correctamente** (verificado con ffprobe), pero necesitas usar un reproductor especializado.

### ✅ Métodos de Reproducción Recomendados

#### 1. VLC Media Player (Más Simple)
1. Descarga VLC: https://www.videolan.org/
2. Abre VLC
3. Ve a **Media → Abrir ubicación de red**
4. Pega la URL del stream:
   ```
   http://localhost:6880/live/admin/Admin2024!Secure/[CHANNEL_ID].ts
   ```
5. Reemplaza `[CHANNEL_ID]` con el ID del canal (ej: 1, 22, etc.)
6. Haz clic en **Reproducir**

**Ejemplo**:
```
http://localhost:6880/live/admin/Admin2024!Secure/22.ts
```

#### 2. Cliente IPTV (Mejor Experiencia)

**Android/Android TV**:
- **IPTV Smarters Pro** (Recomendado)
- **TiviMate** (Mejor EPG)
- **Perfect Player** (Ligero)

**iOS/Apple TV**:
- **IPTV Smarters Pro**
- **GSE Smart IPTV**

**Windows/Mac/Linux**:
- **VLC Media Player**
- **Kodi** (con addon PVR IPTV Simple Client)

**Smart TV**:
- **Smart IPTV** (Samsung/LG)
- **SS IPTV**

**Configuración en Cliente IPTV**:
1. Selecciona "Xtream Codes API" o "Add Xtream Codes"
2. Introduce:
   - **URL**: http://localhost:6880 (o tu IP local)
   - **Usuario**: admin
   - **Contraseña**: Admin2024!Secure
3. Los canales se cargarán automáticamente organizados por categorías

#### 3. Desde el Dashboard Web

El dashboard web ahora muestra:
- ✅ Información del canal
- ✅ URL del stream para copiar
- ✅ Instrucciones de reproducción
- ✅ Botón para abrir el stream en VLC u otro reproductor

**Pasos**:
1. Accede a http://localhost:6880
2. Ve a la sección **Channels**
3. Haz clic en el botón **Play** (▶️) del canal
4. Copia la URL del stream
5. Pégala en VLC o tu reproductor favorito

## 🔧 Verificación de Streams

Para verificar que un stream funciona correctamente, usa ffprobe:

```bash
ffprobe http://localhost:6880/live/admin/Admin2024!Secure/22.ts
```

Deberías ver información del video (H.264) y audio (AAC) si el stream está funcionando.

## 🔧 Endpoints de la API

### API Principal
- **Health Check**: http://localhost:6880/health
- **Documentación API**: http://localhost:6880/docs

### Xtream Codes API
- **Player API**: http://localhost:6880/player_api.php
- **Get Categories**: http://localhost:6880/player_api.php?username=admin&password=Admin2024!Secure&action=get_live_categories
- **Get Streams**: http://localhost:6880/player_api.php?username=admin&password=Admin2024!Secure&action=get_live_streams

### AceProxy
- **Get Stream**: http://localhost:6880/ace/getstream?id=[ACESTREAM_ID]
- **Status**: http://localhost:6880/ace/status

## 🌐 Acceso Remoto

Para acceder desde otros dispositivos en tu red local:

1. Encuentra tu IP local:
   ```bash
   ipconfig
   ```
   Busca la dirección IPv4 (ej: 192.168.1.100)

2. Usa esa IP en lugar de localhost:
   ```
   http://192.168.1.100:6880
   ```

3. Asegúrate de que el firewall permita conexiones en el puerto 6880

## 🔒 Seguridad

- El dashboard solo es accesible desde localhost por defecto
- Las credenciales están configuradas en el archivo `.env`
- Para cambiar las credenciales, edita `.env` y reinicia los contenedores:
  ```bash
  docker-compose restart
  ```

## 🆘 Solución de Problemas

### No puedo acceder al dashboard
- Verifica que los contenedores estén corriendo: `docker-compose ps`
- Asegúrate de usar http://localhost:6880 (no https)
- Verifica que el puerto 6880 no esté en uso por otra aplicación

### Los canales no cargan
- Verifica que el scraper haya ejecutado: ve a Dashboard → Scraper
- Ejecuta manualmente el scraper si es necesario
- Revisa los logs: `docker-compose logs unified-iptv`

### El stream no reproduce en el navegador
- **Esto es normal**: Los navegadores no soportan MPEG-TS en vivo
- **Solución**: Usa VLC, IPTV Smarters u otro cliente IPTV
- Los streams SÍ funcionan (verificado con ffprobe)

### El stream no reproduce en VLC
- Verifica que AceStream Engine esté corriendo: `docker-compose ps`
- Algunos canales pueden estar offline (depende de la fuente)
- Prueba con otro canal
- Verifica la URL del stream (debe incluir usuario y contraseña)
- Revisa los logs: `docker-compose logs acestream`

### Credenciales incorrectas
- Las credenciales por defecto son:
  - Usuario: admin
  - Contraseña: Admin2024!Secure
- Si las cambiaste, verifica el archivo `.env`

### Cómo verificar que un stream funciona
```bash
# Usar ffprobe para verificar el stream
ffprobe http://localhost:6880/live/admin/Admin2024!Secure/22.ts

# Deberías ver información de video H.264 y audio AAC
```

## 📞 Soporte

Para más información, consulta:
- **README.md**: Documentación general del proyecto
- **INSTALACION-COMPLETA.md**: Guía de instalación detallada
- **API-REFERENCE.md**: Documentación completa de todas las APIs
- **MEJORAS-IMPLEMENTADAS.md**: Historial de cambios y mejoras

---

**Última actualización**: 24 de enero de 2026
