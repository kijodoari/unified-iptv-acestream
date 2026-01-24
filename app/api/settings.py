"""
Settings Management API Endpoints
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.utils.auth import get_db
from app.models import Setting

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic models
class SettingCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str]


@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get all settings"""
    settings = db.query(Setting).order_by(Setting.key).all()
    
    return [
        {
            "id": setting.id,
            "key": setting.key,
            "value": setting.value,
            "description": setting.description
        }
        for setting in settings
    ]


@router.get("/settings/{key}")
async def get_setting(key: str, db: Session = Depends(get_db)):
    """Get single setting by key"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return {
        "id": setting.id,
        "key": setting.key,
        "value": setting.value,
        "description": setting.description
    }


@router.post("/settings")
async def create_setting(setting_data: SettingCreate, db: Session = Depends(get_db)):
    """Create a new setting"""
    # Check if key already exists
    existing = db.query(Setting).filter(Setting.key == setting_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    
    setting = Setting(
        key=setting_data.key,
        value=setting_data.value,
        description=setting_data.description
    )
    
    db.add(setting)
    db.commit()
    db.refresh(setting)
    
    logger.info(f"Setting created: {setting.key}")
    
    return {
        "id": setting.id,
        "key": setting.key,
        "message": "Setting created successfully"
    }


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    db: Session = Depends(get_db)
):
    """Update a setting"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.value = setting_data.value
    if setting_data.description is not None:
        setting.description = setting_data.description
    
    db.commit()
    db.refresh(setting)
    
    logger.info(f"Setting updated: {setting.key}")
    
    return {
        "id": setting.id,
        "key": setting.key,
        "message": "Setting updated successfully"
    }


@router.delete("/settings/{key}")
async def delete_setting(key: str, db: Session = Depends(get_db)):
    """Delete a setting"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    
    logger.info(f"Setting deleted: {key}")
    
    return {"message": "Setting deleted successfully"}


@router.post("/settings/bulk-update")
async def bulk_update_settings(
    settings_data: List[dict],
    db: Session = Depends(get_db)
):
    """Bulk update multiple settings"""
    updated_count = 0
    
    for item in settings_data:
        key = item.get("key")
        value = item.get("value")
        
        if not key or value is None:
            continue
        
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
            updated_count += 1
        else:
            # Create if doesn't exist
            new_setting = Setting(
                key=key,
                value=value,
                description=item.get("description")
            )
            db.add(new_setting)
            updated_count += 1
    
    db.commit()
    
    logger.info(f"Bulk update: {updated_count} settings updated")
    
    return {
        "message": f"{updated_count} settings updated successfully",
        "count": updated_count
    }
