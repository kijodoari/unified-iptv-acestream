"""
API endpoints for EPG Source management
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.utils.auth import get_db
from app.models import EPGSource

router = APIRouter()
logger = logging.getLogger(__name__)


class EPGSourceCreate(BaseModel):
    url: str
    is_enabled: bool = True


class EPGSourceUpdate(BaseModel):
    url: Optional[str] = None
    is_enabled: Optional[bool] = None


@router.get("/epg/sources")
async def list_epg_sources(include_deleted: bool = False, db: Session = Depends(get_db)):
    """List all EPG sources (excluding deleted by default)"""
    query = db.query(EPGSource)
    
    if not include_deleted:
        query = query.filter(EPGSource.is_deleted == False)
    
    sources = query.order_by(EPGSource.id).all()
    
    return [
        {
            "id": source.id,
            "url": source.url,
            "is_enabled": source.is_enabled,
            "is_deleted": source.is_deleted,
            "last_updated": source.last_updated.isoformat() if source.last_updated else None,
            "programs_found": source.programs_found,
            "created_at": source.created_at.isoformat(),
            "deleted_at": source.deleted_at.isoformat() if source.deleted_at else None
        }
        for source in sources
    ]


@router.post("/epg/sources")
async def create_epg_source(source_data: EPGSourceCreate, db: Session = Depends(get_db)):
    """Create a new EPG source"""
    
    # Check if URL already exists
    existing = db.query(EPGSource).filter(EPGSource.url == source_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already exists")
    
    # Create new source
    source = EPGSource(
        url=source_data.url,
        is_enabled=source_data.is_enabled
    )
    
    db.add(source)
    db.commit()
    db.refresh(source)
    
    logger.info(f"Created EPG source: {source.url}")
    
    return {
        "id": source.id,
        "url": source.url,
        "message": "EPG source created successfully"
    }


@router.put("/epg/sources/{source_id}")
async def update_epg_source(
    source_id: int,
    source_data: EPGSourceUpdate,
    db: Session = Depends(get_db)
):
    """Update an EPG source"""
    
    source = db.query(EPGSource).filter(EPGSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="EPG source not found")
    
    # Update fields
    if source_data.url is not None:
        # Check if new URL already exists
        existing = db.query(EPGSource).filter(
            EPGSource.url == source_data.url,
            EPGSource.id != source_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="URL already exists")
        source.url = source_data.url
    
    if source_data.is_enabled is not None:
        source.is_enabled = source_data.is_enabled
    
    db.commit()
    db.refresh(source)
    
    logger.info(f"Updated EPG source {source_id}: {source.url}")
    
    return {
        "id": source.id,
        "url": source.url,
        "message": "EPG source updated successfully"
    }


@router.delete("/epg/sources/{source_id}")
async def delete_epg_source(source_id: int, db: Session = Depends(get_db)):
    """Delete an EPG source (soft delete)"""
    
    source = db.query(EPGSource).filter(EPGSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="EPG source not found")
    
    url = source.url
    
    # Soft delete: marcar como eliminada en lugar de borrar
    from datetime import datetime
    source.is_deleted = True
    source.is_enabled = False
    source.deleted_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Soft deleted EPG source {source_id}: {url}")
    
    return {
        "message": "EPG source deleted successfully"
    }
