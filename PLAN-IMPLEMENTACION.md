# Plan de Implementación - Funcionalidades Pendientes

**Fecha**: 24 de enero de 2026  
**Proyecto**: Unified AceStream Platform  
**Versión**: 1.0.0

---

## 📋 Resumen Ejecutivo

Este documento detalla el plan completo para implementar las 4 interfaces de usuario y 4 funcionalidades backend que están pendientes en la plataforma.

### Estado Actual
- ✅ Dashboard principal funcional
- ✅ Gestión de canales completa
- ✅ Reproductor HLS en navegador
- ✅ API Xtream Codes funcional
- ❌ 4 interfaces de usuario incompletas
- ❌ 4 funcionalidades backend pendientes

---

## 🎯 Funcionalidades Pendientes

### Interfaces de Usuario (Frontend)
1. **User Management** - Gestión completa de usuarios
2. **Settings** - Configuración del sistema
3. **EPG Management** - Gestión de guía electrónica
4. **Scraper Management** - Gestión de scraping

### Funcionalidades Backend (API)
5. **EPG Update Trigger** - Actualización manual de EPG
6. **Channel Status Check** - Verificación de estado de canales
7. **VOD Support** - Soporte para Video On Demand
8. **Series Support** - Soporte para series de TV

---

## 📦 FASE 1: User Management (Gestión de Usuarios)

### Prioridad: ALTA
### Tiempo estimado: 3-4 horas
### Dependencias: Ninguna

### 1.1 Backend - Endpoints API

**Archivo**: `app/api/users.py` (NUEVO)

```python
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
    new_password: str,
    db: Session = Depends(get_db)
):
    """Reset user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
```

### 1.2 Frontend - Template HTML

**Archivo**: `app/templates/users.html` (REEMPLAZAR)

```html
{% extends "layout.html" %}
{% block title %}Users - Unified AceStream Platform{% endblock %}
{% block users_active %}active{% endblock %}
{% block page_title %}User Management{% endblock %}

{% block page_actions %}
<button class="btn btn-primary" onclick="showAddUserModal()">
    <i class="bi bi-plus-circle"></i> Add User
</button>
{% endblock %}

{% block content %}
<div class="card mb-4">
    <div class="card-header">
        <div class="row align-items-center">
            <div class="col">
                <h5 class="mb-0">All Users</h5>
            </div>
            <div class="col-auto">
                <div class="input-group input-group-sm">
                    <span class="input-group-text">
                        <i class="bi bi-search"></i>
                    </span>
                    <input type="text" class="form-control" id="searchInput" 
                           placeholder="Search users..." onkeyup="filterUsers()">
                </div>
            </div>
        </div>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover" id="usersTable">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Max Connections</th>
                        <th>Expiry</th>
                        <th>Last Login</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="8" class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
async function loadUsers() {
    try {
        const response = await fetch('/api/users?limit=100');
        const users = await response.json();
        
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = '';
        
        if (users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center">
                        <div class="empty-state">
                            <i class="bi bi-people"></i>
                            <p>No users found. Add your first user.</p>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            users.forEach(user => {
                const row = document.createElement('tr');
                
                const userType = user.is_admin ? 'Admin' : (user.is_trial ? 'Trial' : 'Regular');
                const userTypeBadge = user.is_admin ? 'bg-danger' : (user.is_trial ? 'bg-warning' : 'bg-info');
                
                const expiryDate = user.expiry_date ? new Date(user.expiry_date).toLocaleDateString() : 'Never';
                const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString() : 'Never';
                
                row.innerHTML = `
                    <td><strong>${user.username}</strong></td>
                    <td>${user.email || '<span class="text-muted">N/A</span>'}</td>
                    <td><span class="badge ${userTypeBadge}">${userType}</span></td>
                    <td>
                        <span class="badge ${user.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>${user.max_connections}</td>
                    <td>${expiryDate}</td>
                    <td>${lastLogin}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-info" onclick="editUser(${user.id})" title="Edit">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-warning" onclick="resetPassword(${user.id})" title="Reset Password">
                                <i class="bi bi-key"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteUser(${user.id})" title="Delete">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showAlert('Error loading users', 'danger');
    }
}

function filterUsers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#usersTable tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function showAddUserModal() {
    const modalHtml = `
        <div class="modal fade" id="addUserModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New User</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="addUserForm">
                            <div class="mb-3">
                                <label class="form-label">Username *</label>
                                <input type="text" class="form-control" id="addUsername" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password *</label>
                                <input type="password" class="form-control" id="addPassword" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Email</label>
                                <input type="email" class="form-control" id="addEmail">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Max Connections</label>
                                <input type="number" class="form-control" id="addMaxConnections" value="1" min="1">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Expiry (days)</label>
                                <input type="number" class="form-control" id="addExpiryDays" placeholder="Leave empty for no expiry">
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input" id="addIsAdmin">
                                    <label class="form-check-label" for="addIsAdmin">Administrator</label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input type="checkbox" class="form-check-input" id="addIsTrial">
                                    <label class="form-check-label" for="addIsTrial">Trial User</label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Notes</label>
                                <textarea class="form-control" id="addNotes" rows="2"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="addUser()">Add User</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    const existingModal = document.getElementById('addUserModal');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
    modal.show();
}

async function addUser() {
    try {
        const data = {
            username: document.getElementById('addUsername').value,
            password: document.getElementById('addPassword').value,
            email: document.getElementById('addEmail').value || null,
            max_connections: parseInt(document.getElementById('addMaxConnections').value),
            expiry_days: document.getElementById('addExpiryDays').value ? parseInt(document.getElementById('addExpiryDays').value) : null,
            is_admin: document.getElementById('addIsAdmin').checked,
            is_trial: document.getElementById('addIsTrial').checked,
            notes: document.getElementById('addNotes').value || null
        };
        
        if (!data.username || !data.password) {
            showAlert('Username and password are required', 'warning');
            return;
        }
        
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add user');
        }
        
        showAlert('User added successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addUserModal')).hide();
        loadUsers();
        
    } catch (error) {
        console.error('Error adding user:', error);
        showAlert('Error adding user: ' + error.message, 'danger');
    }
}

async function editUser(id) {
    // Similar implementation to addUser but for editing
    showAlert('Edit user functionality - to be implemented', 'info');
}

async function resetPassword(id) {
    const newPassword = prompt('Enter new password for user:');
    if (!newPassword) return;
    
    try {
        const response = await fetch(`/api/users/${id}/reset-password`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({new_password: newPassword})
        });
        
        if (!response.ok) throw new Error('Failed to reset password');
        
        showAlert('Password reset successfully', 'success');
    } catch (error) {
        console.error('Error resetting password:', error);
        showAlert('Error resetting password: ' + error.message, 'danger');
    }
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
        const response = await fetch(`/api/users/${id}`, {method: 'DELETE'});
        if (!response.ok) throw new Error('Failed to delete user');
        
        showAlert('User deleted successfully', 'success');
        loadUsers();
    } catch (error) {
        console.error('Error deleting user:', error);
        showAlert('Error deleting user: ' + error.message, 'danger');
    }
}

// Load users on page load
loadUsers();

// Refresh every minute
setInterval(loadUsers, 60000);
</script>
{% endblock %}
```

### 1.3 Integración en main.py

**Archivo**: `main.py` (AGREGAR)

```python
# Agregar después de las otras importaciones de routers
from app.api import users

# Agregar después de incluir otros routers
app.include_router(users.router, prefix="/api", tags=["users"])
```

---

## 📦 FASE 2-4: Settings, EPG, Scraper

*[Continúa con estructura similar para las otras 3 fases...]*

---

## 🔧 Orden de Implementación Recomendado

1. **User Management** (FASE 1) - Base para todo
2. **Settings** (FASE 2) - Configuración del sistema
3. **Scraper Management** (FASE 3) - Gestión de fuentes
4. **EPG Management** (FASE 4) - Guía de programación
5. **Backend APIs** (FASE 5-8) - Funcionalidades adicionales

---

## ✅ Checklist de Implementación

### Por cada fase:
- [ ] Crear/modificar archivos backend
- [ ] Crear/modificar templates HTML
- [ ] Integrar en main.py
- [ ] Compilar Docker
- [ ] Probar funcionalidad
- [ ] Documentar en MEJORAS-IMPLEMENTADAS.md
- [ ] Commit y push

---

**Nota**: Este es el plan para la FASE 1. ¿Quieres que continúe con las fases 2-8 completas?
