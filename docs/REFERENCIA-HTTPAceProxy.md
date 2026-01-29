# 📚 Documentación Completa: HTTPAceProxy (pepsik-kiev)

**Proyecto de Referencia**: https://github.com/pepsik-kiev/HTTPAceProxy  
**Ubicación Local**: `reference-HTTPAceProxy/`  
**Estado**: ✅ Activo y mantenido  
**Última actualización**: 25 de enero de 2026

---

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
4. [Configuración](#configuración)
5. [Plugins Disponibles](#plugins-disponibles)
6. [Módulos Principales](#módulos-principales)
7. [Características Avanzadas](#características-avanzadas)
8. [Comparación con Nuestra Implementación](#comparación-con-nuestra-implementación)

---

## 📖 Descripción General

HTTPAceProxy es un proxy HTTP para Ace Stream que permite:
- Ver streams en vivo de Ace Stream sobre HTTP
- Reproducir archivos BitTorrent sobre HTTP
- Soporte para múltiples formatos: Content-ID (PIDs), .acelive, infohash, torrents
- Plugins para SmartTV, KODI, VLC, TorrentTV, AllFon, Torrent Monitor

**⚠️ Advertencia Legal**: Ten cuidado al ver archivos torrent. Puedes recibir abusos de copyright con multas enormes dependiendo de la legislación de tu país.

---

## 🔧 Requisitos del Sistema

### Versiones de Python Soportadas
- **Python 2**: >= 2.7.10
- **Python 3**: >= 3.4 ✅
- **PyPy**: 2.7(3.6)

### Dependencias Obligatorias
```
gevent >= 1.3.3
psutil >= 5.3.0
```

### Dependencias Opcionales (Altamente Recomendadas)
- **ffmpeg**: Para transcodificación
- **VLC**: Para transcodificación y multiplexing

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Carpetas

```
reference-HTTPAceProxy/
├── acehttp.py              # Servidor HTTP principal (gevent)
├── aceconfig.py            # Configuración del usuario (editable)
├── acedefconfig.py         # Configuración por defecto (NO editar)
├── aceclient/              # Cliente para comunicación con AceStream Engine
│   ├── acemessages.py      # Mensajes del protocolo AceStream
│   └── clientcounter.py    # Contador de clientes conectados
├── http/                   # Módulos HTTP
├── modules/                # Módulos auxiliares
│   ├── colorer.py          # Coloreado de logs
│   ├── getmac.py           # Obtención de MAC address
│   ├── ipaddr.py           # Manejo de direcciones IP
│   ├── playlist.py         # Generación de playlists
│   ├── PlaylistGenerator.py # Generador avanzado de playlists
│   ├── requests_file.py    # Manejo de archivos con requests
│   ├── socks.py            # Soporte SOCKS proxy
│   ├── utils.py            # Utilidades generales
│   └── wheels/             # Dependencias empaquetadas
└── plugins/                # Sistema de plugins
    ├── allfon_plugin.py    # Plugin para AllFon TV
    ├── frytv_plugin.py     # Plugin para FryTV
    ├── p2pproxy_plugin.py  # Plugin P2P Proxy
    ├── stat_plugin.py      # Plugin de estadísticas
    ├── torrentfilms_plugin.py # Plugin para Torrent Films
    ├── torrenttelik_plugin.py # Plugin para Torrent Telik
    ├── torrenttv_api.py    # API de TorrentTV
    ├── torrenttv_plugin.py # Plugin para TorrentTV
    └── config/             # Configuraciones de plugins
```

---

## ⚙️ Configuración

### Archivo: `aceconfig.py`

#### 1. Configuración de AceStream Engine

```python
# Spawn automático del engine
acespawn = False

# Comando para iniciar AceStream (Linux)
acecmd = '/opt/acestream/start-engine --client-console --live-buffer 25 --vod-buffer 10'

# API Key de AceStream
acekey = 'n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'

# Configuración de conexión
ace = {
    'aceHostIP': '127.0.0.1',
    'aceAPIport': '62062',
    'aceHTTPport': '6878'
}

# Parámetros demográficos
aceage = AceConst.AGE_35_44
acesex = AceConst.SEX_MALE

# Timeouts
acestartuptimeout = 15  # Timeout de inicio
aceconntimeout = 5      # Timeout de conexión
aceresulttimeout = 10.0 # Timeout de respuesta
```

#### 2. Tipo de Stream

```python
# HTTP (recomendado)
acestreamtype = {'output_format': 'http'}

# HLS con transcodificación
acestreamtype = {
    'output_format': 'hls',
    'transcode_audio': 0,
    'transcode_mp3': 0,
    'transcode_ac3': 0,
    'preferred_audio_language': 'rus'
}
```

#### 3. Seek Back Feature

```python
# Retroceso en segundos (ayuda con lags)
# ⚠️ NO usar con HLS
videoseekback = 0

# Timeout para URL reproducible
videotimeout = 60
```

#### 4. Configuración del Servidor HTTP

```python
# Host del servidor
httphost = 'auto'  # 'auto', '0.0.0.0', o IP específica

# Puerto del servidor
httpport = 8000  # 8081 recomendado para SmartTV con TTV widget

# Usuario para drop privileges (si se inicia como root)
aceproxyuser = ''

# Conexiones concurrentes máximas
maxconns = 10

# Transfer-encoding chunked
use_chunked = True
```

#### 5. Firewall

```python
# Habilitar firewall
firewall = False

# Modo: True = blacklist, False = whitelist
firewallblacklistmode = False

# Rangos de red permitidos/bloqueados
firewallnetranges = (
    '127.0.0.1',
    '192.168.0.0/16',
)
```

#### 6. Transcodificación

```python
transcodecmd = {}

# Usando ffmpeg
transcodecmd['100k'] = 'ffmpeg -i - -c:a copy -b 100k -f mpegts -'.split()
transcodecmd['mp2'] = 'ffmpeg -i - -c:a mp2 -c:v mpeg2video -f mpegts -qscale:v 2 -'.split()
transcodecmd['mkv'] = 'ffmpeg -i - -map 0 -c:a copy -c:a copy -f matroska -'.split()
transcodecmd['default'] = 'ffmpeg -i - -map 0 -c:a copy -c:v copy -f mpegts -'.split()

# Usando VLC
transcodecmd['mp4'] = 'cvlc --rc-fake-tty - --sout-all --sout=#transcode{vcodec=h264,vb=1024,acodec=mp4a,ab=192,channels=2,deinterlace}:std{access=file,mux=ts{use-key-frames},dst=-}'.split()
transcodecmd['default'] = 'cvlc - --sout-all --sout=#std{access=file,mux=ts{use-key-frames},dst=-}'.split()
```

#### 7. Logging

```python
# Nivel de log
loglevel = logging.INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Formato de log
logfmt = '%(filename)-15.15s [LINE:%(lineno)-4s]# %(levelname)-8s [%(asctime)s] %(message)s'

# Formato de fecha
logdatefmt = '%d.%m %H:%M:%S'

# Archivo de log (None = consola)
logfile = None
```

#### 8. Detección de Fake Requests

```python
@staticmethod
def isFakeRequest(path, params, headers):
    '''
    Detecta requests falsos de Smart TVs y STBs
    '''
    useragent = headers.get('User-Agent')
    
    # Samsung ES series
    if useragent == 'Lavf/55.33.100' and headers.get('Range') != 'bytes=0-':
        return True
    
    # Samsung H series
    elif useragent == 'Lavf52.104.0' and headers.get('Range') != 'bytes=0-':
        return True
    
    # LG Netacast 2013
    elif useragent == 'GStreamer souphttpsrc (compatible; LG NetCast.TV-2013) libsoup/2.34.2' and headers.get('icy-metadata') != '1':
        return True
    
    # Samsung K series
    elif useragent == 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebKit/538.1 (KHTML, like Gecko) Version/2.4.0 TV Safari/538.1' and 'Range' in headers and not 'accept-encoding' in headers:
        return True
    
    # Dune 301
    elif useragent == 'DuneHD/1.0' and headers.get('Range') != 'bytes=0-':
        return True
    
    # MX Player 1.10.xx for Android
    elif 'MXPlayer/1.10.' in useragent and 'Accept-Encoding' in headers:
        return True
    
    return False
```

---

## 🔌 Plugins Disponibles

### 1. **TorrentTV Plugin** (`torrenttv_plugin.py`)
- Integración con TorrentTV.ru
- API completa para canales
- Generación de playlists M3U

### 2. **AllFon Plugin** (`allfon_plugin.py`)
- Integración con AllFon TV
- Soporte para canales de AllFon

### 3. **P2P Proxy Plugin** (`p2pproxy_plugin.py`)
- Proxy P2P para SmartTV
- Compatible con widget TTV
- Puerto recomendado: 8081

### 4. **Stat Plugin** (`stat_plugin.py`)
- Estadísticas de uso
- Monitoreo de conexiones
- Métricas de rendimiento

### 5. **Torrent Films Plugin** (`torrentfilms_plugin.py`)
- Integración con servicios de películas torrent

### 6. **Torrent Telik Plugin** (`torrenttelik_plugin.py`)
- Integración con Torrent Telik

### 7. **FryTV Plugin** (`frytv_plugin.py`)
- Integración con FryTV

### Estructura de un Plugin

```python
class PluginInterface:
    def __init__(self, AceConfig, AceStuff):
        self.AceConfig = AceConfig
        self.AceStuff = AceStuff
    
    def handle(self, connection):
        # Lógica del plugin
        pass
```

---

## 📦 Módulos Principales

### 1. **acehttp.py** - Servidor HTTP Principal

**Framework**: gevent (asíncrono)

**Características**:
- Servidor HTTP basado en gevent.server.StreamServer
- Pool de greenlets para concurrencia
- Manejo de requests GET/HEAD
- Detección de fake requests
- Firewall integrado
- Logging avanzado

**Clase Principal**: `HTTPHandler(BaseHTTPRequestHandler)`

### 2. **aceclient/** - Cliente AceStream

**Archivos**:
- `acemessages.py`: Protocolo de mensajes AceStream
- `clientcounter.py`: Contador de clientes conectados

**Funcionalidad**:
- Comunicación con AceStream Engine
- Manejo de sesiones
- Control de streams

### 3. **modules/utils.py** - Utilidades

**Funciones**:
- `schedule()`: Programación de tareas
- `query_get()`: Parsing de query strings
- Manejo de URLs
- Helpers generales

### 4. **modules/playlist.py** - Generación de Playlists

**Formatos soportados**:
- M3U
- M3U8
- XSPF

**Características**:
- Generación dinámica
- Metadata completa
- Logos y EPG

### 5. **modules/PlaylistGenerator.py** - Generador Avanzado

**Características**:
- Generación de playlists complejas
- Filtrado de canales
- Ordenamiento
- Categorización

### 6. **modules/ipaddr.py** - Manejo de IPs

**Funcionalidades**:
- Parsing de direcciones IP
- Rangos de red
- Validación
- Comparación

### 7. **modules/colorer.py** - Coloreado de Logs

**Características**:
- Logs coloreados en consola
- Niveles de log con colores
- Mejor legibilidad

---

## 🚀 Características Avanzadas

### 1. **Multiplexing**

HTTPAceProxy soporta múltiples clientes viendo el mismo stream:
- Requiere VLC para funcionar correctamente
- Reduce carga en AceStream Engine
- Ahorra ancho de banda

### 2. **Transcodificación en Tiempo Real**

Usando ffmpeg o VLC:
```bash
# URL con transcodificación
http://localhost:8000/channels/?type=m3u&fmt=mp2
```

Parámetro `fmt` selecciona el comando de transcodificación.

### 3. **HLS Streaming**

Soporte para HLS con opciones de transcodificación:
- Transcode audio a AAC
- Transcode MP3
- Transcode AC3
- Selección de idioma de audio

### 4. **Seek Back**

Retroceso automático del stream:
- Ayuda a combatir lags de AceStream
- Introduce delay en el video
- Solo funciona con HTTP (no HLS)

### 5. **Firewall Integrado**

Dos modos:
- **Whitelist**: Solo IPs permitidas
- **Blacklist**: Todas excepto bloqueadas

Soporte para rangos de red CIDR.

### 6. **Detección de Fake Requests**

Detecta y maneja requests falsos de:
- Samsung Smart TVs (ES, H, K series)
- LG Netcast TVs
- Dune HD players
- MX Player Android
- Otros STBs

### 7. **Sistema de Plugins**

Arquitectura extensible:
- Plugins independientes
- Configuración por plugin
- Fácil desarrollo de nuevos plugins

---

## 🔄 Comparación con Nuestra Implementación

| Aspecto | HTTPAceProxy | Nuestra Implementación |
|---------|--------------|------------------------|
| **Framework** | gevent | FastAPI + aiohttp |
| **Arquitectura** | Monolítico | Microservicios (capas) |
| **Async** | gevent greenlets | asyncio nativo |
| **API** | HTTP básico | REST API + OpenAPI |
| **Base de Datos** | No tiene | SQLAlchemy + SQLite |
| **Dashboard** | No tiene | Web UI completo |
| **Plugins** | Sistema de plugins | Servicios integrados |
| **Scraping** | Plugins externos | Servicio integrado |
| **EPG** | No integrado | Servicio completo |
| **Users** | No tiene | Sistema completo |
| **Xtream API** | No tiene | Implementación completa |
| **Transcodificación** | ffmpeg/VLC | No (streaming directo) |
| **Multiplexing** | Sí (con VLC) | Sí (nativo) |
| **Configuración** | Archivo Python | .env + API dinámica |
| **Documentación** | README básico | Completa (múltiples docs) |
| **Testing** | No tiene | Scripts de prueba |
| **Docker** | No oficial | Docker Compose completo |

### Ventajas de HTTPAceProxy

1. ✅ **Transcodificación**: Soporte completo con ffmpeg/VLC
2. ✅ **HLS**: Streaming HLS nativo
3. ✅ **Plugins**: Sistema extensible de plugins
4. ✅ **Seek Back**: Feature único para combatir lags
5. ✅ **Fake Request Detection**: Manejo de Smart TVs

### Ventajas de Nuestra Implementación

1. ✅ **Arquitectura Moderna**: FastAPI + asyncio
2. ✅ **API REST**: Documentada con OpenAPI
3. ✅ **Dashboard Web**: Interfaz de administración
4. ✅ **Base de Datos**: Persistencia de datos
5. ✅ **Scraping Integrado**: Recolección automática
6. ✅ **EPG Completo**: Guía de programación
7. ✅ **Xtream API**: Compatibilidad IPTV
8. ✅ **Users Management**: Sistema de usuarios
9. ✅ **Settings Dinámicos**: Configuración en tiempo real
10. ✅ **Docker**: Despliegue simplificado

---

## 📝 Conclusiones

### ¿Cuándo Usar HTTPAceProxy?

- Necesitas transcodificación avanzada
- Requieres HLS streaming
- Quieres usar plugins específicos (TorrentTV, AllFon)
- Necesitas seek back para combatir lags
- Prefieres configuración en Python

### ¿Cuándo Usar Nuestra Implementación?

- Necesitas una plataforma IPTV completa
- Requieres dashboard web
- Quieres API REST moderna
- Necesitas gestión de usuarios
- Requieres scraping automático
- Quieres EPG integrado
- Prefieres Docker y despliegue simple

### Posibles Mejoras a Implementar

De HTTPAceProxy podríamos adoptar:

1. **Transcodificación**: Integrar ffmpeg para transcodificación opcional
2. **HLS Support**: Añadir soporte para HLS streaming
3. **Seek Back**: Implementar feature de retroceso
4. **Fake Request Detection**: Mejorar detección de Smart TVs
5. **Plugin System**: Sistema de plugins extensible

---

## 📚 Referencias

- **Repositorio**: https://github.com/pepsik-kiev/HTTPAceProxy
- **Ubicación Local**: `reference-HTTPAceProxy/`
- **Documentación Original**: `reference-HTTPAceProxy/README.md`
- **Configuración**: `reference-HTTPAceProxy/aceconfig.py`

---

**Fecha de Documentación**: 25 de enero de 2026  
**Autor**: Kiro AI Assistant  
**Proyecto**: Unified IPTV AceStream Platform
