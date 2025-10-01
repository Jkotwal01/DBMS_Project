# services/faculty_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas
from services.user_service import UserService

class FacultyService:
    """Service layer for faculty-related operations"""
    
    @staticmethod
    def create_faculty(db: Session, faculty_data: schemas.FacultyCreate) -> models.Faculty:
        """Create a new faculty with user account"""
        # Create user first
        user = UserService.create_user(db, faculty_data.user)
        
        # Create faculty profile
        faculty = models.Faculty(
            faculty_id=user.user_id,
            employee_id=faculty_data.employee_id,
            designation=faculty_data.designation,
            dept=faculty_data.dept,
            specialization=faculty_data.specialization,
            joining_date=faculty_data.joining_date
        )
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
        return faculty
    
    @staticmethod
    def get_faculty_by_id(db: Session, faculty_id: int) -> Optional[models.Faculty]:
        """Get faculty by ID with user details"""
        return db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
    
    @staticmethod
    def get_faculty_by_employee_id(db: Session, employee_id: str) -> Optional[models.Faculty]:
        """Get faculty by employee ID"""
        return db.query(models.Faculty).filter(models.Faculty.employee_id == employee_id).first()
    
    @staticmethod
    def update_faculty(db: Session, faculty_id: int, faculty_data: schemas.FacultyUpdate) -> models.Faculty:
        """Update faculty profile"""
        faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
        if not faculty:
            raise ValueError("Faculty not found")
        
        for key, value in faculty_data.dict(exclude_unset=True).items():
            setattr(faculty, key, value)
        
        db.commit()
        db.refresh(faculty)
        return faculty
    
    @staticmethod
    def delete_faculty(db: Session, faculty_id: int) -> bool:
        """Delete faculty and associated user account"""
        faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
        if not faculty:
            raise ValueError("Faculty not found")
        
        # Delete user (cascade will delete faculty)
        return UserService.delete_user(db, faculty_id)
    
    @staticmethod
    def get_all_faculty(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        dept: Optional[str] = None
    ) -> List[models.Faculty]:
        """Get all faculty with optional filters"""
        query = db.query(models.Faculty)
        
        if dept:
            query = query.filter(models.Faculty.dept == dept)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_faculty_profile(db: Session, user_id: int, profile_data: schemas.FacultyProfileUpdate) -> models.Faculty:
        """Create faculty profile for existing user"""
        faculty = models.Faculty(
            faculty_id=user_id,
            employee_id=profile_data.employee_id,
            designation=profile_data.designation,
            dept=profile_data.dept,
            specialization=profile_data.specialization,
            joining_date=profile_data.joining_date
        )
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
        return faculty
