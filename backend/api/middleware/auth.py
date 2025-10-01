# api/middleware/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from database import SessionLocal
from models import User, RoleEnum
from auth import decode_access_token
import functools

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token and return current authenticated user.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Check if user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(allowed_roles: List[str]):
    """
    Dependency to check if user has required role.
    
    Usage:
        @app.get("/admin/users", dependencies=[Depends(require_role(["Admin"]))])
        
    Args:
        allowed_roles: List of role names that are allowed
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        user_role = current_user.role.value
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Convenient role checkers for single roles
def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Require Student role"""
    if current_user.role.value != "Student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Student role required."
        )
    return current_user

def require_faculty(current_user: User = Depends(get_current_user)) -> User:
    """Require Faculty role"""
    if current_user.role.value != "Faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Faculty role required."
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require Admin role"""
    if current_user.role.value != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

def require_faculty_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require Faculty or Admin role"""
    if current_user.role.value not in ["Faculty", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Faculty or Admin role required."
        )
    return current_user

# Permission-based decorator for more granular control
class Permission:
    """Permission constants for fine-grained access control"""
    # Student permissions
    VIEW_OWN_ATTENDANCE = "view_own_attendance"
    VIEW_OWN_TIMETABLE = "view_own_timetable"
    EDIT_OWN_PROFILE = "edit_own_profile"
    VIEW_NOTIFICATIONS = "view_notifications"
    
    # Faculty permissions
    MANAGE_ATTENDANCE = "manage_attendance"
    MANAGE_TIMETABLE = "manage_timetable"
    MANAGE_STUDENTS = "manage_students"
    SEND_NOTIFICATIONS = "send_notifications"
    VIEW_ALL_STUDENTS = "view_all_students"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SUBJECTS = "manage_subjects"
    MANAGE_FACULTY = "manage_faculty"
    VIEW_REPORTS = "view_reports"
    SYSTEM_CONFIG = "system_config"

# Role-Permission mapping (can be moved to database for dynamic permissions)
ROLE_PERMISSIONS = {
    "Student": [
        Permission.VIEW_OWN_ATTENDANCE,
        Permission.VIEW_OWN_TIMETABLE,
        Permission.EDIT_OWN_PROFILE,
        Permission.VIEW_NOTIFICATIONS,
    ],
    "Faculty": [
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_TIMETABLE,
        Permission.MANAGE_STUDENTS,
        Permission.SEND_NOTIFICATIONS,
        Permission.VIEW_ALL_STUDENTS,
        Permission.EDIT_OWN_PROFILE,
        Permission.VIEW_NOTIFICATIONS,
    ],
    "Admin": [
        Permission.MANAGE_USERS,
        Permission.MANAGE_SUBJECTS,
        Permission.MANAGE_FACULTY,
        Permission.MANAGE_STUDENTS,
        Permission.VIEW_REPORTS,
        Permission.SYSTEM_CONFIG,
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_TIMETABLE,
        Permission.SEND_NOTIFICATIONS,
        Permission.VIEW_ALL_STUDENTS,
    ],
}

def has_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    user_role = user.role.value
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission: str):
    """
    Dependency to check if user has specific permission.
    
    Usage:
        @app.post("/students", dependencies=[Depends(require_permission(Permission.MANAGE_STUDENTS))])
    """
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {permission}"
            )
        return current_user
    return permission_checker
