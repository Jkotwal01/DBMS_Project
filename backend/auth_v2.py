# auth_v2.py - Enhanced Authentication and Security
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class SecurityManager:
    """Enhanced security manager for authentication and authorization"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        """Generate password reset token"""
        data = {
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        }
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[str]:
        """Verify password reset token and return email"""
        payload = SecurityManager.verify_token(token, "password_reset")
        if payload:
            return payload.get("email")
        return None

# Role-based Access Control
class RBACManager:
    """Role-Based Access Control Manager"""
    
    # Define permissions for each role
    ROLE_PERMISSIONS = {
        "Student": [
            "read_own_profile",
            "update_own_profile",
            "read_own_attendance",
            "read_timetable",
            "read_notifications"
        ],
        "Faculty": [
            "read_own_profile",
            "update_own_profile",
            "read_student_profiles",
            "update_student_profiles",
            "mark_attendance",
            "read_attendance",
            "create_notifications",
            "read_notifications",
            "manage_timetable",
            "upload_student_data",
            "read_departments",
            "read_subjects"
        ],
        "Admin": [
            "read_all_profiles",
            "update_all_profiles",
            "create_users",
            "delete_users",
            "manage_departments",
            "manage_subjects",
            "manage_academic_years",
            "manage_semesters",
            "read_audit_logs",
            "system_settings",
            "bulk_operations"
        ],
        "Parent": [
            "read_child_profile",
            "read_child_attendance",
            "read_child_timetable",
            "read_notifications"
        ],
        "Management": [
            "read_all_profiles",
            "read_reports",
            "read_analytics",
            "read_departments",
            "read_financial_data"
        ]
    }
    
    # Define resource access rules
    RESOURCE_ACCESS = {
        "users": {
            "Student": ["read_own", "update_own"],
            "Faculty": ["read_own", "update_own", "read_students", "update_students"],
            "Admin": ["read_all", "update_all", "create", "delete"],
            "Parent": ["read_children"],
            "Management": ["read_all"]
        },
        "attendance": {
            "Student": ["read_own"],
            "Faculty": ["read_all", "create", "update"],
            "Admin": ["read_all", "create", "update", "delete"],
            "Parent": ["read_children"],
            "Management": ["read_all"]
        },
        "notifications": {
            "Student": ["read"],
            "Faculty": ["read", "create"],
            "Admin": ["read_all", "create", "update", "delete"],
            "Parent": ["read"],
            "Management": ["read_all"]
        },
        "departments": {
            "Faculty": ["read"],
            "Admin": ["read_all", "create", "update", "delete"],
            "Management": ["read_all"]
        },
        "subjects": {
            "Faculty": ["read", "update_own"],
            "Admin": ["read_all", "create", "update", "delete"],
            "Management": ["read_all"]
        }
    }
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def can_access_resource(cls, role: str, resource: str, action: str) -> bool:
        """Check if role can perform action on resource"""
        resource_access = cls.RESOURCE_ACCESS.get(resource, {})
        role_access = resource_access.get(role, [])
        
        # Check for specific action or wildcard
        return action in role_access or "all" in role_access
    
    @classmethod
    def get_role_hierarchy(cls, role: str) -> int:
        """Get role hierarchy level (higher number = more privileges)"""
        hierarchy = {
            "Student": 1,
            "Parent": 2,
            "Faculty": 3,
            "Admin": 4,
            "Management": 5
        }
        return hierarchy.get(role, 0)
    
    @classmethod
    def can_access_user_data(cls, requester_role: str, target_role: str, requester_id: int, target_id: int) -> bool:
        """Check if user can access another user's data"""
        # Users can always access their own data
        if requester_id == target_id:
            return True
        
        # Check role hierarchy
        requester_level = cls.get_role_hierarchy(requester_role)
        target_level = cls.get_role_hierarchy(target_role)
        
        # Higher level roles can access lower level data
        if requester_level > target_level:
            return True
        
        # Faculty can access student data
        if requester_role == "Faculty" and target_role == "Student":
            return True
        
        # Parents can access their children's data (would need additional relationship check)
        if requester_role == "Parent" and target_role == "Student":
            return True  # This should be further validated with parent-student relationship
        
        return False

# Authentication Middleware
class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    @staticmethod
    async def get_current_user(token: str = None, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        if not token:
            return None
        
        payload = SecurityManager.verify_token(token, "access")
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        # Get user from database
        from crud_v2 import user_crud
        user = user_crud.get_by_id(db, user_id)
        if not user or user.status != "Active":
            return None
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
            "status": user.status.value
        }
    
    @staticmethod
    def require_auth(current_user: Dict[str, Any] = None):
        """Require authentication"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
    
    @staticmethod
    def require_role(allowed_roles: list):
        """Require specific role(s)"""
        def role_checker(current_user: Dict[str, Any] = None):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            return current_user
        return role_checker
    
    @staticmethod
    def require_permission(permission: str):
        """Require specific permission"""
        def permission_checker(current_user: Dict[str, Any] = None):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get("role")
            if not RBACManager.has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required permission: {permission}"
                )
            return current_user
        return permission_checker
    
    @staticmethod
    def require_resource_access(resource: str, action: str):
        """Require access to specific resource and action"""
        def access_checker(current_user: Dict[str, Any] = None):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get("role")
            if not RBACManager.can_access_resource(user_role, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to {resource} for {action}"
                )
            return current_user
        return access_checker

# Audit Logging
class AuditLogger:
    """Audit logging for security events"""
    
    @staticmethod
    def log_login(db: Session, user_id: int, ip_address: str, user_agent: str, success: bool, failure_reason: str = None):
        """Log login attempt"""
        from models_v2 import LoginLog
        
        login_log = LoginLog(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_successful=success,
            failure_reason=failure_reason
        )
        db.add(login_log)
        db.commit()
    
    @staticmethod
    def log_activity(db: Session, user_id: int, action: str, table_name: str, record_id: int = None, 
                    old_values: Dict = None, new_values: Dict = None, ip_address: str = None):
        """Log user activity"""
        from models_v2 import AuditLog
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()

# Rate Limiting
class RateLimiter:
    """Simple rate limiting implementation"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if request is allowed based on rate limit"""
        import time
        
        current_time = time.time()
        window_start = current_time - window
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check limit
        if len(self.requests[identifier]) >= limit:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True

# Initialize security components
security_manager = SecurityManager()
rbac_manager = RBACManager()
auth_middleware = AuthMiddleware()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()