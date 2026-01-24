"""
User Management API Endpoints
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.utils.auth import get_db, get_password_hash, verify_password
from app.models import User, UserActivity

router = APIRouter()
logger = logging.getLogger(__name__)


# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    is_admin: bool = False
    is_trial: bool = False
    max_connections: int = 1
    expiry_days: Optional[int] = None
    notes: Optional[str] = None


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_trial: Optional[bool] = None
    max_connections: Optional[int] = None
    expiry_days: Optional[int] = None
    notes: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    is_admin: bool
    is_trial: bool
    max_connections: int
    expiry_date: Optional[datetime]
    created_at: datetime
    last_login: Optional[datetime]
    notes: Optional[str]


@router.get("/users")
async def get_users(
    limit: int = 100,
    offset: int = 0,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get list of users"""
    query = db.query(User)
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "is_trial": user.is_trial,
            "max_connections": user.max_connections,
            "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "notes": user.notes
        }
        for user in users
    ]


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get single user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent activities
    activities = db.query(UserActivity).filter(
        UserActivity.user_id == user_id
    ).order_by(UserActivity.created_at.desc()).limit(10).all()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_trial": user.is_trial,
        "max_connections": user.max_connections,
        "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "notes": user.notes,
        "recent_activities": [
            {
                "type": activity.activity_type,
                "description": activity.description,
                "ip_address": activity.ip_address,
                "created_at": activity.created_at.isoformat()
            }
            for activity in activities
        ]
    }


@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Calculate expiry date
    expiry_date = None
    if user_data.expiry_days:
        expiry_date = datetime.utcnow() + timedelta(days=user_data.expiry_days)
    
    # Create user
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        is_admin=user_data.is_admin,
        is_trial=user_data.is_trial,
        max_connections=user_data.max_connections,
        expiry_date=expiry_date,
        notes=user_data.notes
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="user_created",
        description=f"User {user.username} created"
    )
    db.add(activity)
    db.commit()
    
    logger.info(f"User created: {user.username} (ID: {user.id})")
    
    return {
        "id": user.id,
        "username": user.username,
        "message": "User created successfully"
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)
    
    if user_data.email is not None:
        # Check if email already exists for another user
        if user_data.email:
            existing = db.query(User).filter(
                User.email == user_data.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data.email
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    if user_data.is_trial is not None:
        user.is_trial = user_data.is_trial
    
    if user_data.max_connections is not None:
        user.max_connections = user_data.max_connections
    
    if user_data.expiry_days is not None:
        user.expiry_date = datetime.utcnow() + timedelta(days=user_data.expiry_days)
    
    if user_data.notes is not None:
        user.notes = user_data.notes
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="user_updated",
        description=f"User {user.username} updated"
    )
    db.add(activity)
    db.commit()
    
    logger.info(f"User updated: {user.username} (ID: {user.id})")
    
    return {
        "id": user.id,
        "username": user.username,
        "message": "User updated successfully"
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    username = user.username
    
    db.delete(user)
    db.commit()
    
    logger.info(f"User deleted: {username} (ID: {user_id})")
    
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db)
):
    """Reset user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(status_code=400, detail="new_password is required")
    
    user.password_hash = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="password_reset",
        description=f"Password reset for user {user.username}"
    )
    db.add(activity)
    db.commit()
    
    logger.info(f"Password reset for user: {user.username} (ID: {user.id})")
    
    return {"message": "Password reset successfully"}
