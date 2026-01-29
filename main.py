"""
Main application entry point for Unified AceStream Platform
"""
import asyncio
import logging
import sys
import os
import time
import hashlib
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from sqlalchemy.orm import Session

from setup import main as setup_app
from app.config import get_config
from app.utils.auth import create_user
from app.services.aceproxy_service import AceProxyService
from app.services.aiohttp_streaming_server import AiohttpStreamingServer
from app.services.scraper_service import ImprovedScraperService
from app.services.epg_service import EPGService
from app.api import xtream
from app.api import dashboard
from app.api import api_endpoints
from app.api import aceproxy
from app.api import logs
from app.api import users
from app.api import settings
from app.api import scraper
from app.api import epg
from app.models import User, ScraperURL, EPGSource, Setting

# Optional import for acestream_search
try:
    from acestream_search import main as engine, get_options, __version__
    ACESTREAM_SEARCH_AVAILABLE = True
except ImportError:
    engine = None
    get_options = None
    __version__ = "N/A"
    ACESTREAM_SEARCH_AVAILABLE = False
    import warnings
    warnings.warn("acestream_search module not available. Search functionality will be disabled.")

# Get base directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)
(STATIC_DIR / "favicon").mkdir(exist_ok=True)

# Ensure logs directory exists
(BASE_DIR / "logs").mkdir(exist_ok=True)

# Get config to determine log level
from app.config import get_config
config = get_config()

# Configure logging with force=True to override any existing config
# Use DEBUG level if server_debug is enabled, otherwise INFO
log_level = logging.DEBUG if config.server_debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(BASE_DIR / 'logs/app.log'), mode='a')
    ],
    force=True
)

logger = logging.getLogger(__name__)


# Global services
aceproxy_service: AceProxyService = None
aiohttp_streaming_server: AiohttpStreamingServer = None
scraper_service: ImprovedScraperService = None  # Using improved scraper
epg_service: EPGService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global aceproxy_service, aiohttp_streaming_server, scraper_service, epg_service
    
    logger.info("Starting Unified AceStream Platform...")
    
    # Initialize configuration first
    config = get_config()
    
    # Run database migrations automatically
    logger.info("Running database migrations...")
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database migrations completed successfully")
    except Exception as e:
        logger.warning(f"Migration warning (may be first run): {e}")
        # If migrations fail, try to stamp the database
        try:
            from alembic.config import Config
            from alembic import command
            
            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, "head")
            logger.info("✅ Database stamped with current schema")
        except Exception as stamp_error:
            logger.warning(f"Could not stamp database: {stamp_error}")
    
    # Initialize database with config
    from app.utils.auth import init_db as initialize_database
    initialize_database()
    
    # Now we can import SessionLocal
    from app.utils.auth import SessionLocal
    
    # Create database session for initialization
    db = SessionLocal()
    
    try:
        # Check/create admin user
        admin = db.query(User).filter(User.is_admin == True).first()
        if not admin:
            logger.info("Creating admin user...")
            create_user(
                db,
                username=config.admin_username,
                password=config.admin_password,
                is_admin=True
            )
            logger.info(f"Admin user created: {config.admin_username}")
        
        # Initialize scraper URLs if configured (smart initialization)
        scraper_urls_list = config.get_scraper_urls_list()
        if scraper_urls_list:
            for url in scraper_urls_list:
                existing = db.query(ScraperURL).filter(ScraperURL.url == url).first()
                if not existing:
                    # URL no existe, crear nueva
                    scraper_url = ScraperURL(url=url, is_enabled=True, is_deleted=False)
                    db.add(scraper_url)
                    logger.info(f"Initialized scraper URL from .env: {url}")
                elif existing.is_deleted:
                    # URL existe pero fue eliminada por usuario, NO recrear
                    logger.info(f"Skipping deleted scraper URL: {url}")
                # Si existe y NO está eliminada, no hacer nada (BD prevalece)
            db.commit()
        
        # Initialize EPG sources if configured (smart initialization)
        epg_sources_list = config.get_epg_sources_list()
        if epg_sources_list:
            for url in epg_sources_list:
                existing = db.query(EPGSource).filter(EPGSource.url == url).first()
                if not existing:
                    # URL no existe, crear nueva
                    epg_source = EPGSource(url=url, is_enabled=True, is_deleted=False)
                    db.add(epg_source)
                    logger.info(f"Initialized EPG source from .env: {url}")
                elif existing.is_deleted:
                    # URL existe pero fue eliminada por usuario, NO recrear
                    logger.info(f"Skipping deleted EPG source: {url}")
                # Si existe y NO está eliminada, no hacer nada (BD prevalece)
            db.commit()
        
        # Initialize default settings if empty
        settings_count = db.query(Setting).count()
        if settings_count == 0:
            logger.info("Initializing default settings...")
            default_settings = [
                # Server Configuration
                Setting(key="server_host", value=config.server_host, description="Host del servidor (0.0.0.0 = todas las interfaces)"),
                Setting(key="server_port", value=str(config.server_port), description="Puerto del servidor web"),
                Setting(key="server_timezone", value=config.server_timezone, description="Zona horaria del servidor"),
                Setting(key="server_debug", value=str(config.server_debug).lower(), description="Modo debug (true/false)"),
                
                # AceStream Engine Configuration
                Setting(key="acestream_enabled", value=str(config.acestream_enabled).lower(), description="Habilitar AceStream Engine (true/false)"),
                Setting(key="acestream_engine_host", value=config.acestream_engine_host, description="Host del AceStream Engine"),
                Setting(key="acestream_engine_port", value=str(config.acestream_engine_port), description="Puerto del AceStream Engine"),
                Setting(key="acestream_timeout", value=str(config.acestream_timeout), description="Timeout de conexión AceStream (segundos)"),
                
                # AceStream Streaming Server (internal)
                Setting(key="acestream_streaming_host", value=config.acestream_streaming_host, description="Host del servidor de streaming interno"),
                Setting(key="acestream_streaming_port", value=str(config.acestream_streaming_port), description="Puerto del servidor de streaming interno"),
                Setting(key="acestream_chunk_size", value=str(config.acestream_chunk_size), description="Tamaño de chunk para streaming (bytes)"),
                Setting(key="acestream_empty_timeout", value=str(config.acestream_empty_timeout), description="Timeout sin datos (segundos)"),
                Setting(key="acestream_no_response_timeout", value=str(config.acestream_no_response_timeout), description="Timeout sin respuesta (segundos)"),
                
                # Scraper Configuration
                Setting(key="scraper_update_interval", value=str(config.scraper_update_interval), description="Intervalo de actualización del scraper (segundos)"),
                
                # EPG Configuration
                Setting(key="epg_update_interval", value=str(config.epg_update_interval), description="Intervalo de actualización EPG (segundos)"),
                Setting(key="epg_cache_file", value=config.epg_cache_file, description="Ruta del archivo de cache EPG"),
                
                # Database Configuration
                Setting(key="database_url", value=config.database_url, description="URL de conexión a la base de datos"),
                Setting(key="database_echo", value=str(config.database_echo).lower(), description="Mostrar queries SQL en logs (true/false)"),
                Setting(key="database_pool_size", value=str(config.database_pool_size), description="Tamaño del pool de conexiones"),
                Setting(key="database_max_overflow", value=str(config.database_max_overflow), description="Máximo de conexiones adicionales"),
                
                # Security
                # Note: admin_username/password se gestionan desde User Management, no desde Settings
                # Note: No guardamos SECRET_KEY en settings por seguridad
                Setting(key="access_token_expire_minutes", value=str(config.access_token_expire_minutes), description="Tiempo de expiración de tokens (minutos)"),
                
                # External Access
                Setting(key="external_url", value="", description="URL externa para acceso remoto (opcional, ej: http://mi-dominio.com:6880)"),
            ]
            
            for setting in default_settings:
                db.add(setting)
            
            db.commit()
            logger.info(f"Created {len(default_settings)} default settings")
        
        # Initialize services
        if config.acestream_enabled:
            logger.info("Starting aiohttp streaming server (native pyacexy pattern)...")
            aiohttp_streaming_server = AiohttpStreamingServer(
                acestream_host=config.acestream_engine_host,
                acestream_port=config.acestream_engine_port,
                listen_host=config.acestream_streaming_host,
                listen_port=config.acestream_streaming_port,
                chunk_size=config.acestream_chunk_size,
                empty_timeout=config.acestream_empty_timeout,
                no_response_timeout=config.acestream_no_response_timeout,
            )
            await aiohttp_streaming_server.start()
            
            # Keep old AceProxyService for compatibility (stats, management API)
            logger.info("Starting AceProxy service (for API/stats)...")
            aceproxy_service = AceProxyService(
                acestream_host=config.acestream_engine_host,
                acestream_port=config.acestream_engine_port,
                timeout=config.acestream_timeout
            )
            await aceproxy_service.start()
            
            # Store in app state
            app.state.aceproxy_service = aceproxy_service
            app.state.aiohttp_streaming_server = aiohttp_streaming_server
        else:
            app.state.aceproxy_service = None
            app.state.aiohttp_streaming_server = None
        
        logger.info("Starting Scraper service...")
        scraper_service = ImprovedScraperService(
            update_interval=config.scraper_update_interval
        )
        await scraper_service.start()
        
        logger.info("Starting EPG service...")
        epg_service = EPGService(db)
        await epg_service.start()
        
        # Start background tasks
        asyncio.create_task(scraper_service.auto_scrape_loop())
        asyncio.create_task(epg_service.auto_update_loop())
        
        logger.info("All services started successfully")
        
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")
    
    if aiohttp_streaming_server:
        await aiohttp_streaming_server.stop()
    
    if aceproxy_service:
        await aceproxy_service.stop()
    
    if scraper_service:
        await scraper_service.stop()
    
    if epg_service:
        await epg_service.stop()
    
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Unified AceStream Platform",
    description="Complete AceStream platform with Xtream Codes API, EPG, and more",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Favicon endpoint
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to avoid 404 errors"""
    favicon_path = STATIC_DIR / "favicon" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/svg+xml")
    # Return 204 No Content if favicon doesn't exist
    return Response(status_code=204)

# Include routers - ORDER MATTERS! Most specific first
# AceProxy routes without prefix for pyacexy compatibility  
app.include_router(aceproxy.router, tags=["AceProxy"])
app.include_router(logs.router, prefix="/api", tags=["Logs"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])
app.include_router(scraper.router, prefix="/api", tags=["Scraper"])
app.include_router(epg.router, prefix="/api", tags=["EPG"])
app.include_router(api_endpoints.router, prefix="/api", tags=["API"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(xtream.router, tags=["Xtream API"])  # Last because it catches all paths

# Health check endpoint
@app.get("/health")
@app.get("/api/health")
async def health_check(request: Request):
    """Health check endpoint"""
    config = get_config()
    
    health_status = {
        "status": "healthy",
        "services": {
            "aceproxy": aceproxy_service is not None if config.acestream_enabled else "disabled",
            "scraper": scraper_service is not None,
            "epg": epg_service is not None
        }
    }
    
    # Get service statistics from aiohttp streaming server
    active_streams_count = 0
    if config.acestream_enabled and aiohttp_streaming_server:
        try:
            # Quick lock to get count only
            async with aiohttp_streaming_server.streams_lock:
                active_streams_count = len(aiohttp_streaming_server.streams)
        except Exception as e:
            logger.error(f"Error getting stream count: {e}")
    
    health_status["aceproxy_streams"] = active_streams_count
    
    return health_status

@app.get('/m3u')
async def search(request: Request):
    args = get_args(request)
    # return str(args)
    if args.xml_epg:
        content_type = 'text/xml'
    elif args.json:
        content_type = 'application/json'
    else:
        content_type = 'application/x-mpegURL'

    CACHE_DIR = 'tmp/cache'
    CACHE_EXPIRY = 300
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    def generate():               
        cache_key = hashlib.md5(str(args).encode('utf-8')).hexdigest()
        cache_file = os.path.join(CACHE_DIR, cache_key)
        temp_cache_file = cache_file + '.tmp'
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < CACHE_EXPIRY:
            with open(cache_file, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line
        else:
            if not ACESTREAM_SEARCH_AVAILABLE:
                raise HTTPException(status_code=503, detail="AceStream search functionality is not available. Module 'acestream_search' is not installed.")
            
            try:
                with open(temp_cache_file, 'w', encoding='utf-8') as f:                              
                    for page in engine(args):
                        f.write(page + '\n')
                os.rename(temp_cache_file, cache_file)
            finally: 
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        yield line

    if 'version' in args:
        return Response(__version__ + '\n', media_type='text/plain')
    if 'help' in args:
        return Response(args.help, media_type='text/plain')
    if 'usage' in args:
        return Response(args.usage, media_type='text/plain')
    if args.url:
        redirect_url = next(x for x in generate()).strip('\n')
        response = Response('', media_type='')
        response.headers['Location'] = redirect_url
        response.headers['Content-Type'] = ''
        response.status_code = 302
        return response
    return Response(''.join(generate()), media_type=content_type)

@app.get("/")
async def root():
    """Root endpoint"""
    config = get_config()
    
    return {
        "name": "Unified AceStream Platform",
        "version": "1.0.0",
        "endpoints": {
            "xtream_api": f"http://{config.server_host}:{config.server_port}/player_api.php",
            "m3u_playlist": f"http://{config.server_host}:{config.server_port}/get.php",
            "epg": f"http://{config.server_host}:{config.server_port}/xmltv.php",
            "aceproxy": f"http://{config.server_host}:{config.server_port}/ace/getstream",
            "health": "/health",
            "docs": "/docs"
        }
    }

def get_args(request: Request):
    opts = {'prog': str(request.base_url)}
    for item in request.query_params:
        opts[item] = request.query_params[item]
    if 'query' not in opts:
        opts['query'] = ''
    args = get_options(opts)
    return args

def get_content_id(infohash: str) -> str:
    """Fetch content_id for a given infohash from the acestream engine API."""
    import requests
    try:
        url = f"http://{config.acestream_engine_host}:{config.acestream_engine_port}/server/api"
        params = {
            "api_version": 3,
            "method": "get_content_id",
            "infohash": infohash
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("result", {}).get("content_id")
    except Exception as e:       
        return str(e)

if __name__ == "__main__":
    import uvicorn
    
    setup_app()  # Run setup on startup
    config = get_config()
    
    # Configure uvicorn logging to also write to file
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["handlers"]["file"] = {
        "class": "logging.FileHandler",
        "filename": str(BASE_DIR / "logs/app.log"),
        "formatter": "default",
        "mode": "a"
    }
    log_config["loggers"]["uvicorn"]["handlers"].append("file")
    log_config["loggers"]["uvicorn.access"]["handlers"].append("file")
    
    # Run unified server on single port
    # Use debug log level if server_debug is enabled
    uvicorn_log_level = "debug" if config.server_debug else "info"
    uvicorn.run(
        "main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.server_debug,
        log_level=uvicorn_log_level,
        log_config=log_config
    )
