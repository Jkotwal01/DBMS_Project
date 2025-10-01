# services/user_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas
from auth import hash_password, verify_password

class UserService:
    """Service layer for user-related operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: schemas.UserCreate) -> models.User:
        """Create a new user"""
        # Check if user already exists
        existing = db.query(models.User).filter(models.User.email == user_data.email).first()
        if existing:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = models.User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            department=user_data.department,
            phone=user_data.phone,
            address=user_data.address
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
        """Authenticate user with email and password"""
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
        """Get user by ID"""
        return db.query(models.User).filter(models.User.user_id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        """Get user by email"""
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate) -> models.User:
        """Update user information"""
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> models.User:
        """Soft delete user by setting is_active to False"""
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Hard delete user"""
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[models.User]:
        """Get all users with optional filtering by role"""
        query = db.query(models.User)
        if role:
            query = query.filter(models.User.role == role)
        return query.offset(skip).limit(limit).all()
