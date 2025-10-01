# deps.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, RoleEnum, Permission, UserPermission
from auth import decode_access_token
from schemas import TokenData
import typing
from typing import List, Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from auth import decode_access_token
    from sqlalchemy.exc import NoResultFound
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != role:
            raise HTTPException(status_code=403, detail=f"Operation allowed only for {role}")
        return current_user
    return role_checker

def require_roles(roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(status_code=403, detail=f"Operation allowed only for {', '.join(roles)}")
        return current_user
    return role_checker

def require_permission(resource: str, action: str):
    def permission_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Check if user has specific permission
        user_permissions = db.query(UserPermission).join(Permission).filter(
            UserPermission.user_id == current_user.user_id,
            Permission.resource == resource,
            Permission.action == action
        ).first()
        
        if not user_permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Permission denied: {action} on {resource}"
            )
        return current_user
    return permission_checker

def require_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User account is deactivated")
    return current_user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User account is deactivated")
    return current_user

def is_admin_or_faculty(current_user: User = Depends(get_current_user)):
    if current_user.role.value not in ["Admin", "Faculty"]:
        raise HTTPException(status_code=403, detail="Admin or Faculty access required")
    return current_user

def is_admin(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
