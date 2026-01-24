# Guía Completa de Instalación y Despliegue
## Unified IPTV AceStream Platform

**Repositorio**: https://github.com/TokyoghoulEs/unified-iptv-acestream

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Configuración Inicial](#configuración-inicial)
4. [Compilación de la Imagen Docker](#compilación-de-la-imagen-docker)
5. [Creación y Despliegue de Contenedores](#creación-y-despliegue-de-contenedores)
6. [Verificación del Despliegue](#verificación-del-despliegue)
7. [Acceso a la Plataforma](#acceso-a-la-plataforma)
8. [Documentos de Referencia](#documentos-de-referencia)
9. [Solución de Problemas](#solución-de-problemas)

---

## 1. Requisitos Previos

### Software Necesario

- **Docker Desktop** (Windows/Mac) o **Docker Engine** (Linux)
  - Versión mínima: 20.10+
  - Docker Compose incluido
- **Git** (para clonar el repositorio)
- **Editor de texto** (para modificar archivos de configuración)

### Verificar Instalación de Docker

```bash
docker --version
docker-compose --version
```

Deberías ver algo como:
```
Docker version 24.0.x
Docker Compose version v2.x.x
```

---

## 2. Preparación del Entorno

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/TokyoghoulEs/unified-iptv-acestream.git
cd unified-iptv-acestream
```

### Paso 2: Estructura del Proyecto

El proyecto tiene la siguiente estructura:

```
unified-iptv-acestream/
├── app/                      # Código fuente de la aplicación
│   ├── api/                  # Endpoints de la API
│   ├── models/               # Modelos de base de datos
│   ├── repositories/         # Capa de acceso a datos
│   ├── services/             # Lógica de negocio
│   ├── static/               # Archivos estáticos (CSS, JS)
│   ├── templates/            # Plantillas HTML
│   ├── utils/                # Utilidades
│   └── config.py             # Configuración
├── data/                     # Base de datos (se crea automáticamente)
├── logs/                     # Logs de la aplicación (se crea automáticamente)
├── .env.example              # Ejemplo de configuración
├── .env                      # Configuración real (crear desde .env.example)
├── docker-compose.yml        # Orquestación de contenedores
├── Dockerfile                # Definición de la imagen Docker
├── main.py                   # Punto de entrada
├── requirements.txt          # Dependencias Python
└── README.md                 # Documentación del proyecto
```

---

## 3. Configuración Inicial

### Paso 1: Crear el Archivo de Configuración

Copia el archivo de ejemplo y crea tu configuración:

```bash
# En Windows PowerShell
Copy-Item .env.example .env

# En Linux/Mac
cp .env.example .env
```

### Paso 2: Configurar Variables de Entorno

Edita el archivo `.env` con un editor de texto. Las variables críticas que DEBES cambiar son:

```env
# Admin User (for dashboard access)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=TuPasswordSegura123!

# Security
SECRET_KEY=genera-una-clave-secreta-larga-y-aleatoria-de-64-caracteres-minimo
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### Paso 3: Configuración de AceStream

En el archivo `.env`, asegúrate de que el host de AceStream apunte al contenedor:

```env
# AceStream Configuration
ACESTREAM_ENABLED=true
ACESTREAM_ENGINE_HOST=acestream
ACESTREAM_ENGINE_PORT=6878
ACESTREAM_TIMEOUT=15
```

**Nota**: `acestream` es el nombre del servicio en `docker-compose.yml`, Docker lo resuelve automáticamente.

### Paso 4: Configuración del Servidor

```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=6880
SERVER_TIMEZONE=Europe/Madrid
SERVER_DEBUG=false
```

### Configuración Completa del .env

Aquí está la configuración completa utilizada en este despliegue:

```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=6880
SERVER_TIMEZONE=Europe/Rome
SERVER_DEBUG=false

# AceStream Configuration
ACESTREAM_ENABLED=true
ACESTREAM_ENGINE_HOST=acestream
ACESTREAM_ENGINE_PORT=6878
ACESTREAM_TIMEOUT=15

# AceStream Streaming Server (internal)
ACESTREAM_STREAMING_HOST=127.0.0.1
ACESTREAM_STREAMING_PORT=6881
ACESTREAM_CHUNK_SIZE=8192
ACESTREAM_EMPTY_TIMEOUT=60.0
ACESTREAM_NO_RESPONSE_TIMEOUT=10.0

# Scraper Configuration
SCRAPER_URLS=https://wafy80.github.io/m3u
SCRAPER_UPDATE_INTERVAL=86400

# EPG Configuration
EPG_SOURCES=https://wafy80.github.io/epg_light.xml
EPG_UPDATE_INTERVAL=86400
EPG_CACHE_FILE=data/epg.xml

# Database Configuration
DATABASE_URL=sqlite:///data/unified-iptv.db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Admin User (for dashboard access)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin2024!Secure

# Security
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c03a0a8c9f8e7d8b6c5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

---

## 4. Compilación de la Imagen Docker

### Paso 1: Entender el Dockerfile

El `Dockerfile` define cómo se construye la imagen de la aplicación:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6880

CMD ["python", "main.py"]
```

**Explicación:**
- Usa Python 3.9 slim como base
- Instala las dependencias desde `requirements.txt`
- Copia todo el código de la aplicación
- Expone el puerto 6880
- Ejecuta `main.py` al iniciar el contenedor

### Paso 2: Compilar la Imagen

Ejecuta el siguiente comando para compilar la imagen Docker:

```bash
docker-compose build
```

**Proceso de compilación:**
1. Docker descarga la imagen base `python:3.9-slim`
2. Instala todas las dependencias de `requirements.txt`
3. Copia el código de la aplicación al contenedor
4. Crea la imagen final

**Tiempo estimado**: 2-5 minutos (dependiendo de tu conexión a internet)

**Salida esperada:**
```
[+] Building 45.2s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.9-slim
 => [1/5] FROM docker.io/library/python:3.9-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY . .
 => exporting to image
 => => naming to docker.io/library/unified-iptv-acestream-unified-iptv
```

---

## 5. Creación y Despliegue de Contenedores

### Paso 1: Entender el docker-compose.yml

El archivo `docker-compose.yml` define dos servicios:

```yaml
version: '3.8'

services:
  unified-iptv:
    build: .
    ports:
      - "6880:6880"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - ACESTREAM_ENGINE_HOST=acestream
    depends_on:
      - acestream
    restart: unless-stopped
    
  acestream:
    image: wafy80/acestream
    restart: unless-stopped
```

**Servicios:**

1. **unified-iptv**: La aplicación principal
   - Construida desde el Dockerfile local
   - Puerto 6880 expuesto al host
   - Volúmenes montados para persistencia de datos
   - Depende del servicio acestream

2. **acestream**: Motor AceStream
   - Usa imagen pre-construida `wafy80/acestream`
   - Puerto 6878 interno (no expuesto al host)
   - Se comunica con unified-iptv a través de la red Docker

### Paso 2: Crear y Levantar los Contenedores

Ejecuta el siguiente comando:

```bash
docker-compose up -d
```

**El flag `-d`** significa "detached mode" (modo desacoplado), los contenedores corren en segundo plano.

**Proceso de despliegue:**

1. **Descarga de imágenes** (primera vez):
   - Descarga la imagen `wafy80/acestream` (~167 MB)
   - Tiempo estimado: 1-3 minutos

2. **Creación de red Docker**:
   - Crea una red interna para comunicación entre contenedores
   - Nombre: `unified-iptv-acestream_default`

3. **Creación de contenedores**:
   - `unified-iptv-acestream-acestream-1`
   - `unified-iptv-acestream-unified-iptv-1`

4. **Inicio de servicios**:
   - AceStream Engine inicia primero
   - Aplicación principal espera a que AceStream esté listo
   - Inicialización de base de datos
   - Carga de canales y EPG

**Salida esperada:**
```
[+] Running 3/3
 ✔ Network unified-iptv-acestream_default          Created
 ✔ Container unified-iptv-acestream-acestream-1    Started
 ✔ Container unified-iptv-acestream-unified-iptv-1 Started
```

---

## 6. Verificación del Despliegue

### Paso 1: Verificar Estado de los Contenedores

```bash
docker-compose ps
```

**Salida esperada:**
```
NAME                                    STATUS                    PORTS
unified-iptv-acestream-acestream-1      Up (healthy)              6878/tcp
unified-iptv-acestream-unified-iptv-1   Up                        0.0.0.0:6880->6880/tcp
```

**Estados posibles:**
- `Up`: Contenedor funcionando correctamente
- `Up (healthy)`: Contenedor funcionando y pasó health check
- `Restarting`: Contenedor reiniciándose (problema de configuración)
- `Exited`: Contenedor detenido (error crítico)

### Paso 2: Verificar Logs de la Aplicación

```bash
docker-compose logs unified-iptv
```

**Logs esperados (últimas líneas):**
```
unified-iptv-1  | INFO - Starting Unified IPTV AceStream Platform...
unified-iptv-1  | INFO - Starting aiohttp streaming server...
unified-iptv-1  | INFO - Aiohttp streaming server started on 127.0.0.1:6881
unified-iptv-1  | INFO - Starting AceProxy service (for API/stats)...
unified-iptv-1  | INFO - Starting Scraper service...
unified-iptv-1  | INFO - Starting EPG service...
unified-iptv-1  | INFO - Updated 3419 programs from EPG source
unified-iptv-1  | INFO - All services started successfully
unified-iptv-1  | INFO - Uvicorn running on http://0.0.0.0:6880
```

### Paso 3: Verificar Logs de AceStream

```bash
docker-compose logs acestream
```

### Paso 4: Health Check

Verifica que la aplicación responde:

```bash
curl http://localhost:6880/health
```

**Respuesta esperada:**
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

### Paso 5: Verificar en el Navegador

Abre tu navegador y ve a:
```
http://localhost:6880
```

Deberías ver la página principal con información de la API.

---

## 7. Acceso a la Plataforma

### Acceso al Dashboard

**URL**: http://localhost:6880

**Credenciales:**
- Usuario: `admin`
- Contraseña: `Admin2024!Secure` (o la que configuraste en `.env`)

### Documentación Completa de Acceso

Para información detallada sobre cómo acceder a todos los servicios y configurar clientes IPTV, consulta:

📄 **[ACCESO.md](./ACCESO.md)** - Guía completa de acceso y configuración de clientes

Este documento incluye:
- URLs de todos los endpoints
- Configuración para IPTV Smarters, Perfect Player, TiviMate
- Comandos Docker útiles
- Información de seguridad
- Solución de problemas

---

## 8. Documentos de Referencia

### Documentación del Proyecto

1. **[README.md](./README.md)**
   - Descripción general del proyecto
   - Características principales
   - Arquitectura del sistema
   - Métodos de instalación alternativos

2. **[ACCESO.md](./ACCESO.md)**
   - Guía completa de acceso
   - Configuración de clientes IPTV
   - Comandos Docker útiles
   - Credenciales y seguridad

3. **[.env.example](./.env.example)**
   - Plantilla de configuración
   - Descripción de todas las variables de entorno
   - Valores por defecto

### Archivos de Configuración

1. **[docker-compose.yml](./docker-compose.yml)**
   - Definición de servicios
   - Configuración de red y volúmenes
   - Dependencias entre contenedores

2. **[Dockerfile](./Dockerfile)**
   - Definición de la imagen Docker
   - Proceso de construcción
   - Dependencias del sistema

3. **[requirements.txt](./requirements.txt)**
   - Dependencias Python
   - Versiones específicas de paquetes

### Normas de Desarrollo (Steering)

Ubicadas en `.kiro/steering/`:

1. **idioma-español.md**
   - Normas de comunicación en español
   - Convenciones de código y documentación

2. **proyecto-info.md**
   - Información del proyecto
   - Contexto de desarrollo
   - Tecnologías utilizadas

3. **gestion-procesos.md**
   - Gestión de procesos en ejecución
   - Mejores prácticas para comandos largos

---

## 9. Solución de Problemas

### Problema 1: Contenedor unified-iptv se reinicia constantemente

**Síntoma:**
```bash
docker-compose ps
# Muestra: Restarting (1) X seconds ago
```

**Causa**: Configuración inválida en `.env`

**Solución:**
```bash
# Ver los logs para identificar el error
docker-compose logs unified-iptv

# Errores comunes:
# - SECRET_KEY con valor por defecto
# - ADMIN_PASSWORD con valor por defecto
# - ACESTREAM_ENGINE_HOST incorrecto

# Edita .env y corrige los valores
# Luego reinicia:
docker-compose restart
```

### Problema 2: No se puede acceder a http://localhost:6880

**Posibles causas y soluciones:**

1. **Puerto ocupado:**
```bash
# Windows
netstat -ano | findstr :6880

# Linux/Mac
lsof -i :6880

# Solución: Cambia el puerto en docker-compose.yml
ports:
  - "8080:6880"  # Usa 8080 en lugar de 6880
```

2. **Firewall bloqueando:**
```bash
# Windows: Permite el puerto en el firewall
# Linux: 
sudo ufw allow 6880
```

3. **Contenedor no está corriendo:**
```bash
docker-compose ps
docker-compose up -d
```

### Problema 3: Error al compilar la imagen

**Síntoma:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**Solución:**
```bash
# Limpia la caché de Docker
docker system prune -a

# Reconstruye desde cero
docker-compose build --no-cache
```

### Problema 4: AceStream no se conecta

**Síntoma en logs:**
```
ERROR - Failed to connect to AceStream at http://acestream:6878
```

**Solución:**
```bash
# Verifica que el contenedor acestream esté corriendo
docker-compose ps

# Verifica los logs de acestream
docker-compose logs acestream

# Reinicia ambos servicios
docker-compose restart
```

### Problema 5: Base de datos corrupta

**Síntoma:**
```
ERROR - Database error: database disk image is malformed
```

**Solución:**
```bash
# Detén los contenedores
docker-compose down

# Elimina la base de datos
rm -rf data/unified-iptv.db

# Reinicia (se creará una nueva base de datos)
docker-compose up -d
```

### Problema 6: Permisos en Linux

**Síntoma:**
```
ERROR - Permission denied: '/app/data/unified-iptv.db'
```

**Solución:**
```bash
# Crea el directorio data con permisos correctos
mkdir -p data
chmod 777 data

# Reinicia
docker-compose restart
```

---

## 10. Comandos Útiles de Gestión

### Gestión de Contenedores

```bash
# Ver estado
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f unified-iptv
docker-compose logs -f acestream

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose stop

# Iniciar servicios detenidos
docker-compose start

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar y limpiar volúmenes
docker-compose down -v
```

### Gestión de Imágenes

```bash
# Listar imágenes
docker images

# Eliminar imagen específica
docker rmi unified-iptv-acestream-unified-iptv

# Limpiar imágenes no utilizadas
docker image prune -a
```

### Acceso al Contenedor

```bash
# Acceder a la shell del contenedor
docker-compose exec unified-iptv /bin/bash

# Ejecutar comando en el contenedor
docker-compose exec unified-iptv python --version
```

### Backup y Restauración

```bash
# Backup de la base de datos
docker-compose exec unified-iptv cp /app/data/unified-iptv.db /app/data/backup.db

# Backup completo (desde el host)
tar -czf backup-$(date +%Y%m%d).tar.gz data/ .env

# Restaurar
tar -xzf backup-20260124.tar.gz
docker-compose restart
```

---

## 11. Actualización del Proyecto

### Actualizar desde Git

```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d
```

### Actualizar Solo la Configuración

```bash
# Edita .env
nano .env

# Reinicia sin reconstruir
docker-compose restart
```

---

## 12. Desinstalación Completa

Si necesitas eliminar completamente el proyecto:

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar volúmenes (datos persistentes)
docker-compose down -v

# Eliminar imágenes
docker rmi unified-iptv-acestream-unified-iptv
docker rmi wafy80/acestream

# Eliminar archivos del proyecto
cd ..
rm -rf unified-iptv-acestream
```

---

## 13. Resumen del Proceso Completo

### Comandos Secuenciales para Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/TokyoghoulEs/unified-iptv-acestream.git
cd unified-iptv-acestream

# 2. Crear configuración
cp .env.example .env

# 3. Editar .env (cambiar ADMIN_PASSWORD y SECRET_KEY)
nano .env

# 4. Compilar imagen
docker-compose build

# 5. Levantar contenedores
docker-compose up -d

# 6. Verificar estado
docker-compose ps

# 7. Ver logs
docker-compose logs -f

# 8. Acceder
# Abre http://localhost:6880 en tu navegador
```

---

## 14. Información Adicional

### Puertos Utilizados

| Puerto | Servicio | Acceso | Descripción |
|--------|----------|--------|-------------|
| 6880 | Unified IPTV | Externo | API y Dashboard web |
| 6878 | AceStream Engine | Interno | Motor AceStream (solo entre contenedores) |
| 6881 | Streaming Server | Interno | Servidor de streaming (solo entre contenedores) |

### Volúmenes Docker

| Volumen | Propósito |
|---------|-----------|
| `./data:/app/data` | Base de datos SQLite y archivos de datos |
| `./.env:/app/.env` | Archivo de configuración |

### Red Docker

- **Nombre**: `unified-iptv-acestream_default`
- **Tipo**: Bridge
- **Propósito**: Comunicación entre contenedores

---

## 15. Soporte y Contribuciones

### Repositorio GitHub
https://github.com/TokyoghoulEs/unified-iptv-acestream

### Reportar Problemas
Abre un issue en GitHub con:
- Descripción del problema
- Logs relevantes (`docker-compose logs`)
- Configuración (sin credenciales)
- Sistema operativo y versión de Docker

### Contribuir
1. Fork del repositorio
2. Crea una rama para tu feature
3. Commit de tus cambios
4. Push a tu fork
5. Abre un Pull Request

---

## 16. Licencia

Este proyecto está licenciado bajo MIT License.

**⚠️ Disclaimer**: Este software es para propósitos educativos. Asegúrate de tener los derechos para transmitir el contenido y cumplir con las leyes locales.

---

**Documento creado**: 24 de enero de 2026  
**Versión**: 1.0  
**Autor**: Documentación del proyecto Unified IPTV AceStream Platform

---

## 📚 Índice de Documentos del Proyecto

1. **INSTALACION-COMPLETA.md** (este documento) - Guía completa de instalación
2. **[ACCESO.md](./ACCESO.md)** - Guía de acceso y uso
3. **[MEJORAS-IMPLEMENTADAS.md](./MEJORAS-IMPLEMENTADAS.md)** - Registro de cambios y mejoras
4. **[README.md](./README.md)** - Documentación principal del proyecto
5. **[.env.example](./.env.example)** - Plantilla de configuración

---

¡Gracias por usar Unified IPTV AceStream Platform! 🎉
