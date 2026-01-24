"""
API endpoints for Scraper URL management
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl

from app.utils.auth import get_db
from app.models import ScraperURL

router = APIRouter()
logger = logging.getLogger(__name__)


class ScraperURLCreate(BaseModel):
    url: str
    is_enabled: bool = True


class ScraperURLUpdate(BaseModel):
    url: Optional[str] = None
    is_enabled: Optional[bool] = None


@router.get("/scraper/sources")
async def list_scraper_sources(db: Session = Depends(get_db)):
    """List all scraper sources"""
    sources = db.query(ScraperURL).order_by(ScraperURL.id).all()
    
    return [
        {
            "id": source.id,
            "url": source.url,
            "is_enabled": source.is_enabled,
            "last_scraped": source.last_scraped.isoformat() if source.last_scraped else None,
            "channels_found": source.channels_found,
            "created_at": source.created_at.isoformat()
        }
        for source in sources
    ]


@router.post("/scraper/sources")
async def create_scraper_source(source_data: ScraperURLCreate, db: Session = Depends(get_db)):
    """Create a new scraper source"""
    
    # Check if URL already exists
    existing = db.query(ScraperURL).filter(ScraperURL.url == source_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already exists")
    
    # Create new source
    source = ScraperURL(
        url=source_data.url,
        is_enabled=source_data.is_enabled
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    logger.info(f"Created scraper source: {source.url}")
    
    return {
        "id": source.id,
        "url": source.url,
        "message": "Scraper source created successfully"
    }


@router.put("/scraper/sources/{source_id}")
async def update_scraper_source(
    source_id: int,
    source_data: ScraperURLUpdate,
    db: Session = Depends(get_db)
):
    """Update a scraper source"""
    
    source = db.query(ScraperURL).filter(ScraperURL.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Scraper source not found")
    
    # Update fields
    if source_data.url is not None:
        # Check if new URL already exists
        existing = db.query(ScraperURL).filter(
            ScraperURL.url == source_data.url,
            ScraperURL.id != source_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="URL already exists")
        source.url = source_data.url
    
    if source_data.is_enabled is not None:
        source.is_enabled = source_data.is_enabled
    
    db.commit()
    db.refresh(source)
    
    logger.info(f"Updated scraper source {source_id}: {source.url}")
    
    return {
        "id": source.id,
        "url": source.url,
        "message": "Scraper source updated successfully"
    }


@router.delete("/scraper/sources/{source_id}")
async def delete_scraper_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a scraper source"""
    
    source = db.query(ScraperURL).filter(ScraperURL.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Scraper source not found")
    
    url = source.url
    db.delete(source)
    db.commit()
    
    logger.info(f"Deleted scraper source {source_id}: {url}")
    
    return {
        "message": "Scraper source deleted successfully"
    }
