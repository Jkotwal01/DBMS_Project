# deps_v2.py - Enhanced Dependencies for ERP System
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from database import SessionLocal
import models_v2 as models
from auth_v2 import SecurityManager, AuthMiddleware, RBACManager, AuditLogger, rate_limiter
from schemas_v2 import TokenData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        # Rate limiting
        client_ip = request.client.host
        if not rate_limiter.is_allowed(f"auth_{client_ip}", limit=100, window=3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Verify token
        payload = SecurityManager.verify_token(token, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        from crud_v2 import user_crud
        user = user_crud.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if user.status != models.StatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Log successful authentication
        AuditLogger.log_activity(
            db=db,
            user_id=user.user_id,
            action="authenticate",
            table_name="users",
            record_id=user.user_id,
            ip_address=client_ip
        )
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
            "status": user.status.value,
            "department": user.department
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

def require_role(allowed_roles: List[str]):
    """Dependency to require specific role(s)"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    """Dependency to require specific permission"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if not RBACManager.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {permission}"
            )
        return current_user
    return permission_checker

def require_resource_access(resource: str, action: str):
    """Dependency to require access to specific resource and action"""
    def access_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if not RBACManager.can_access_resource(user_role, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {resource} for {action}"
            )
        return current_user
    return access_checker

# Role-specific dependencies
def require_student_role(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require student role"""
    if current_user.get("role") != "Student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user

def require_faculty_role(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require faculty role"""
    if current_user.get("role") != "Faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faculty access required"
        )
    return current_user

def require_admin_role(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("role") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_parent_role(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require parent role"""
    if current_user.get("role") != "Parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent access required"
        )
    return current_user

def require_management_role(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require management role"""
    if current_user.get("role") != "Management":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management access required"
        )
    return current_user

# Data access dependencies
def get_current_student(
    current_user: Dict[str, Any] = Depends(require_student_role),
    db: Session = Depends(get_db)
):
    """Get current student profile"""
    from crud_v2 import student_crud
    student = student_crud.get_with_user(db, current_user["user_id"])
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    return student

def get_current_faculty(
    current_user: Dict[str, Any] = Depends(require_faculty_role),
    db: Session = Depends(get_db)
):
    """Get current faculty profile"""
    from crud_v2 import faculty_crud
    faculty = faculty_crud.get_with_user(db, current_user["user_id"])
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty profile not found"
        )
    return faculty

def get_current_admin(
    current_user: Dict[str, Any] = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Get current admin profile"""
    from crud_v2 import user_crud
    user = user_crud.get_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_current_parent(
    current_user: Dict[str, Any] = Depends(require_parent_role),
    db: Session = Depends(get_db)
):
    """Get current parent profile"""
    from crud_v2 import user_crud
    user = user_crud.get_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Resource ownership dependencies
def check_user_access(
    target_user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user can access target user's data"""
    from crud_v2 import user_crud
    
    # Get target user
    target_user = user_crud.get_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    # Check access permissions
    requester_role = current_user.get("role")
    target_role = target_user.role.value
    requester_id = current_user.get("user_id")
    
    if not RBACManager.can_access_user_data(
        requester_role, target_role, requester_id, target_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to user data"
        )
    
    return target_user

def check_department_access(
    dept_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user can access department data"""
    from crud_v2 import department_crud
    
    department = department_crud.get(db, dept_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    user_role = current_user.get("role")
    
    # Admin and Management can access all departments
    if user_role in ["Admin", "Management"]:
        return department
    
    # Faculty can access their own department
    if user_role == "Faculty":
        from crud_v2 import faculty_crud
        faculty = faculty_crud.get_with_user(db, current_user["user_id"])
        if faculty and faculty.dept_id == dept_id:
            return department
    
    # Students can access their own department
    if user_role == "Student":
        from crud_v2 import student_crud
        student = student_crud.get_with_user(db, current_user["user_id"])
        if student and student.dept_id == dept_id:
            return department
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied to department data"
    )

def check_subject_access(
    subject_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if current user can access subject data"""
    from crud_v2 import subject_crud
    
    subject = subject_crud.get_with_faculty(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    user_role = current_user.get("role")
    
    # Admin and Management can access all subjects
    if user_role in ["Admin", "Management"]:
        return subject
    
    # Faculty can access their own subjects
    if user_role == "Faculty" and subject.faculty_id == current_user["user_id"]:
        return subject
    
    # Students can access subjects they're enrolled in
    if user_role == "Student":
        from crud_v2 import student_crud
        student = student_crud.get_with_user(db, current_user["user_id"])
        if student:
            # Check if student is enrolled in this subject
            from models_v2 import Enrollment
            enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.student_id,
                Enrollment.subject_id == subject_id
            ).first()
            if enrollment:
                return subject
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied to subject data"
    )

# Audit logging dependency
def log_activity(
    action: str,
    table_name: str,
    record_id: Optional[int] = None,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None
):
    """Dependency to log user activity"""
    def activity_logger(
        request: Request,
        current_user: Dict[str, Any] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        AuditLogger.log_activity(
            db=db,
            user_id=current_user["user_id"],
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.client.host
        )
        return current_user
    return activity_logger

# Pagination dependency
def get_pagination_params(
    skip: int = 0,
    limit: int = 100,
    max_limit: int = 1000
):
    """Pagination parameters dependency"""
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > max_limit:
        limit = min(100, max_limit)
    
    return {"skip": skip, "limit": limit}

# Search and filter dependencies
def get_search_params(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
):
    """Search and sorting parameters dependency"""
    valid_sort_orders = ["asc", "desc"]
    if sort_order not in valid_sort_orders:
        sort_order = "asc"
    
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

# File upload validation
def validate_file_upload(
    file_size: int,
    max_size: int = 10 * 1024 * 1024,  # 10MB default
    allowed_types: List[str] = None
):
    """Validate file upload parameters"""
    if allowed_types is None:
        allowed_types = ["image/jpeg", "image/png", "application/pdf", "text/csv", "application/vnd.ms-excel"]
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes"
        )
    
    return True