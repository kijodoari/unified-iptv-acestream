"""
Web UI Routes for Dashboard
"""
from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import secrets

from app.utils.auth import get_db
from app.models import User, Channel, Category
from app.config import get_config

# Get absolute path to templates directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
security = HTTPBasic()


async def verify_admin_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify admin credentials for dashboard access - authenticates against User table"""
    from app.utils.auth import verify_password
    
    # Find admin user in database
    admin_user = db.query(User).filter(
        User.username == credentials.username,
        User.is_admin == True,
        User.is_active == True
    ).first()
    
    # Verify user exists and password is correct
    if not admin_user or not verify_password(credentials.password, admin_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Update last login
    from datetime import datetime
    admin_user.last_login = datetime.utcnow()
    db.commit()
    
    return credentials.username


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials)
):
    """Dashboard page - requires authentication"""
    config = get_config()
    
    # Get stats
    user_count = db.query(User).count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_count": user_count,
        "server_url": f"http://{config.server_host}:{config.server_port}",
        "timezone": config.server_timezone,
        "acestream_host": config.acestream_engine_host,
        "acestream_port": config.acestream_engine_port,
        "username": username,
    })


@router.get("/channels", response_class=HTMLResponse)
async def channels(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
    username: str = Depends(verify_admin_credentials)
):
    """Channels page - requires authentication"""
    config = get_config()
    return templates.TemplateResponse("channels.html", {
        "request": request,
        "username": username,
        "admin_username": credentials.username,
        "admin_password": credentials.password
    })


@router.get("/users", response_class=HTMLResponse)
async def users(
    request: Request,
    username: str = Depends(verify_admin_credentials)
):
    """Users page - requires authentication"""
    return templates.TemplateResponse("users.html", {
        "request": request,
        "username": username
    })


@router.get("/scraper", response_class=HTMLResponse)
async def scraper(
    request: Request,
    username: str = Depends(verify_admin_credentials)
):
    """Scraper page - requires authentication"""
    return templates.TemplateResponse("scraper.html", {
        "request": request,
        "username": username
    })


@router.get("/epg", response_class=HTMLResponse)
async def epg(
    request: Request,
    username: str = Depends(verify_admin_credentials)
):
    """EPG page - requires authentication"""
    return templates.TemplateResponse("epg.html", {
        "request": request,
        "username": username
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings(
    request: Request,
    username: str = Depends(verify_admin_credentials)
):
    """Settings page - requires authentication"""
    config = get_config()
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": config,
        "username": username
    })
