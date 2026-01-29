# Ejemplos de Uso - Unified IPTV AceStream Platform

## 📖 Guía Rápida de Uso

Este documento contiene ejemplos prácticos paso a paso para usar la plataforma.

---

## 🎯 Caso de Uso 1: Ver un Canal en el Dashboard Web (Más Fácil)

### Paso 1: Acceder al Dashboard
1. Abre el navegador en http://localhost:6880
2. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `Admin2024!Secure`

### Paso 2: Reproducir un Canal
1. Ve a la sección **Channels**
2. Busca el canal que quieres ver
3. Haz clic en el botón **Play** (▶️)
4. El reproductor se abre automáticamente en un modal
5. ¡El canal comienza a reproducirse!

**Ventajas**:
- No necesitas instalar nada
- Reproduce directamente en el navegador
- Interfaz moderna con controles nativos
- Información del canal visible

**Tecnología**:
- Formato: HLS (HTTP Live Streaming)
- Compatible con todos los navegadores modernos

---

## 🎯 Caso de Uso 2: Ver un Canal en VLC (Para Pruebas)

### Paso 1: Obtener la URL del Canal
1. Abre el navegador en http://localhost:6880
2. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `Admin2024!Secure`
3. Ve a la sección **Channels**
4. Busca el canal que quieres ver
5. Haz clic en el botón **Play** (▶️)
6. En el modal que aparece, copia la URL del stream

### Paso 2: Reproducir en VLC
1. Abre VLC Media Player
2. Ve a **Media → Abrir ubicación de red** (o presiona `Ctrl+N`)
3. Pega la URL copiada
4. Haz clic en **Reproducir**

**Ejemplo de URL**:
```
http://localhost:6880/live/admin/Admin2024!Secure/22.ts
```

---

## 🎯 Caso de Uso 3: Configurar IPTV Smarters (Android/iOS)

### Paso 1: Instalar la App
- **Android**: Descarga desde Google Play Store
- **iOS**: Descarga desde App Store
- Busca: "IPTV Smarters Pro"

### Paso 2: Agregar Lista
1. Abre IPTV Smarters Pro
2. Selecciona **Add New User**
3. Elige **Login with Xtream Codes API**
4. Completa los datos:
   - **Name**: Unified IPTV (o el nombre que prefieras)
   - **Username**: `admin`
   - **Password**: `Admin2024!Secure`
   - **URL**: `http://TU_IP_LOCAL:6880` (ej: `http://192.168.1.100:6880`)
5. Haz clic en **Add User**

### Paso 3: Ver Canales
1. Los canales se cargarán automáticamente
2. Navega por categorías
3. Selecciona un canal y reproduce

**Nota**: Si estás en el mismo dispositivo donde corre Docker, usa `http://localhost:6880`

---

## 🎯 Caso de Uso 4: Configurar TiviMate (Android TV)

### Paso 1: Instalar TiviMate
1. Abre Google Play Store en tu Android TV
2. Busca "TiviMate IPTV Player"
3. Instala la aplicación

### Paso 2: Agregar Playlist
1. Abre TiviMate
2. Ve a **Settings → Playlists**
3. Haz clic en **Add Playlist**
4. Selecciona **Xtream Codes**
5. Completa:
   - **Name**: Unified IPTV
   - **Server URL**: `http://TU_IP_LOCAL:6880`
   - **Username**: `admin`
   - **Password**: `Admin2024!Secure`
6. Haz clic en **Next**

### Paso 3: Configurar EPG (Guía de Programación)
1. En la misma pantalla, activa **EPG**
2. La URL del EPG se configura automáticamente
3. Haz clic en **Done**

### Paso 4: Disfrutar
- Los canales aparecerán organizados por categorías
- La guía EPG mostrará la programación
- Puedes grabar programas (función premium)

---

## 🎯 Caso de Uso 5: Usar Playlist M3U en Cualquier Reproductor

### Obtener la Playlist
La URL de la playlist M3U es:
```
http://localhost:6880/get.php?username=admin&password=Admin2024!Secure&type=m3u_plus&output=ts
```

### Usar en VLC
1. Abre VLC
2. Ve a **Media → Abrir ubicación de red**
3. Pega la URL de la playlist
4. VLC cargará todos los canales en la lista de reproducción

### Usar en Kodi
1. Instala el addon **PVR IPTV Simple Client**
2. Ve a **Settings → PVR & Live TV → PVR IPTV Simple Client**
3. En **M3U Play List URL**, pega la URL de la playlist
4. En **EPG Settings → XMLTV URL**, pega:
   ```
   http://localhost:6880/xmltv.php?username=admin&password=Admin2024!Secure
   ```
5. Reinicia Kodi
6. Ve a **TV** para ver los canales

---

## 🎯 Caso de Uso 6: Verificar que un Stream Funciona

### Método 1: Desde el Dashboard (Más Fácil)
1. Ve a http://localhost:6880/channels
2. Haz clic en el botón **Play** (▶️) de cualquier canal
3. Si el reproductor se abre y muestra video = funciona ✅
4. Si no reproduce, prueba otro canal

### Método 2: Usando ffprobe (Técnico)
```bash
ffprobe http://localhost:6880/live/admin/Admin2024!Secure/22.ts
```

**Qué buscar en la salida**:
- `codec_name=h264` - Video H.264 ✅
- `codec_name=aac` - Audio AAC ✅
- `format_name=mpegts` - Formato MPEG-TS ✅
- `width=1280` y `height=720` - Resolución ✅

### Método 3: Usando VLC (Simple)
1. Abre la URL del stream en VLC
2. Si ves video y escuchas audio = funciona ✅
3. Si ves "buffering" constante = el canal puede estar offline o lento

---

## 🎯 Caso de Uso 7: Acceder desde Otro Dispositivo en la Red

### Paso 1: Encontrar tu IP Local
**En Windows**:
```bash
ipconfig
```
Busca la línea que dice `IPv4 Address` (ej: 192.168.1.100)

**En Linux/Mac**:
```bash
ifconfig
```
o
```bash
ip addr show
```

### Paso 2: Configurar Firewall (Windows)
1. Abre **Windows Defender Firewall**
2. Ve a **Configuración avanzada**
3. Crea una nueva regla de entrada:
   - Tipo: Puerto
   - Puerto: 6880
   - Acción: Permitir conexión
   - Perfil: Privado (red local)

### Paso 3: Acceder desde Otro Dispositivo
Usa la IP encontrada en lugar de localhost:
```
http://192.168.1.100:6880
```

**Ejemplo en IPTV Smarters**:
- URL: `http://192.168.1.100:6880`
- Usuario: `admin`
- Contraseña: `Admin2024!Secure`

---

## 🎯 Caso de Uso 8: Agregar Canales Manualmente

### Desde el Dashboard
1. Ve a http://localhost:6880/channels
2. Haz clic en **Add Channel**
3. Completa el formulario:
   - **Name**: Nombre del canal (ej: "La 1 HD")
   - **AceStream ID**: Hash de 40 caracteres del canal
   - **Category**: Categoría (ej: "España", "Deportes")
   - **Logo URL**: URL del logo (opcional)
   - **EPG ID**: ID para la guía EPG (opcional)
4. Haz clic en **Add Channel**

### Ejemplo de AceStream ID
```
cc7b8c39f70aa342248d02c8ab55bafdb4116ed7
```

---

## 🎯 Caso de Uso 9: Configurar Scraper Automático

### Agregar Fuentes de Canales
1. Ve a http://localhost:6880/scraper
2. En la sección **Scraper URLs**, haz clic en **Add URL**
3. Pega la URL de una lista M3U con canales AceStream
4. Haz clic en **Save**

### Ejecutar Scraper Manualmente
1. En la misma página, haz clic en **Run Scraper Now**
2. Espera a que termine (puede tardar varios minutos)
3. Ve a **Channels** para ver los nuevos canales

### Configurar Scraper Automático
El scraper se ejecuta automáticamente cada 24 horas por defecto.

Para cambiar el intervalo, edita `.env`:
```env
SCRAPER_UPDATE_INTERVAL=86400  # 24 horas en segundos
```

---

## 🎯 Caso de Uso 10: Configurar EPG (Guía de Programación)

### Agregar Fuentes EPG
1. Ve a http://localhost:6880/epg
2. Haz clic en **Add EPG Source**
3. Pega la URL de un archivo XMLTV
4. Haz clic en **Save**

### Ejemplo de URL EPG
```
https://wafy80.github.io/epg_light.xml
```

### Actualizar EPG Manualmente
1. En la página de EPG, haz clic en **Update EPG Now**
2. Espera a que descargue y procese el archivo
3. La guía se actualizará automáticamente

---

## 🎯 Caso de Uso 11: Monitorear el Sistema

### Ver Estado del Sistema
1. Ve a http://localhost:6880
2. El dashboard muestra:
   - Total de canales
   - Canales online
   - Última actualización del scraper
   - Última actualización del EPG

### Ver Logs
1. Ve a http://localhost:6880/logs
2. Selecciona el tipo de log:
   - **Application**: Logs de la aplicación
   - **AceStream**: Logs del engine AceStream
   - **Scraper**: Logs del scraper
3. Usa los filtros para buscar errores o eventos específicos

### Verificar Salud de AceStream
```bash
curl http://localhost:6880/health
```

Deberías ver:
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

## 🆘 Solución Rápida de Problemas

### Problema: "No puedo acceder al dashboard"
**Solución**:
```bash
# Verificar que los contenedores están corriendo
docker-compose ps

# Si no están corriendo, iniciarlos
docker-compose up -d

# Verificar logs
docker-compose logs unified-iptv
```

### Problema: "El stream no reproduce"
**Solución**:
1. Verifica que el reproductor del dashboard funciona:
   - Ve a http://localhost:6880/channels
   - Haz clic en Play
   - Si reproduce = el sistema funciona ✅
2. Si no reproduce en el dashboard:
   ```bash
   # Verificar que AceStream Engine está corriendo
   docker-compose ps
   
   # Ver logs de AceStream
   docker-compose logs acestream --tail 50
   ```
3. Si ffprobe muestra video y audio = el stream funciona, usa VLC o cliente IPTV
4. Si ffprobe da error = el canal puede estar offline, prueba otro

### Problema: "No hay canales"
**Solución**:
1. Ve a http://localhost:6880/scraper
2. Verifica que hay URLs de scraper configuradas
3. Haz clic en **Run Scraper Now**
4. Espera a que termine y recarga la página de canales

### Problema: "Credenciales incorrectas"
**Solución**:
Las credenciales por defecto son:
- Usuario: `admin`
- Contraseña: `Admin2024!Secure`

Si las cambiaste, verifica el archivo `.env`

---

## 📚 Recursos Adicionales

### Documentación
- **README.md**: Información general del proyecto
- **INSTALACION-COMPLETA.md**: Guía de instalación paso a paso
- **ACCESO.md**: Guía completa de acceso y configuración
- **API-REFERENCE.md**: Documentación de todas las APIs
- **MEJORAS-IMPLEMENTADAS.md**: Historial de cambios

### APIs Útiles
- **Health Check**: http://localhost:6880/health
- **API Docs**: http://localhost:6880/docs
- **Playlist M3U**: http://localhost:6880/get.php?username=admin&password=Admin2024!Secure&type=m3u_plus&output=ts
- **EPG XMLTV**: http://localhost:6880/xmltv.php?username=admin&password=Admin2024!Secure

### Comandos Docker Útiles
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f unified-iptv

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Iniciar servicios
docker-compose up -d

# Rebuild y reiniciar
docker-compose down
docker-compose build
docker-compose up -d
```

---

**Última actualización**: 24 de enero de 2026
