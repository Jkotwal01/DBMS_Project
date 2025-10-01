# services/subject_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas

class SubjectService:
    """Service layer for subject-related operations"""
    
    @staticmethod
    def create_subject(db: Session, subject_data: schemas.SubjectCreate) -> models.Subject:
        """Create a new subject"""
        # Check if subject code already exists
        if subject_data.subject_code:
            existing = db.query(models.Subject).filter(
                models.Subject.subject_code == subject_data.subject_code
            ).first()
            if existing:
                raise ValueError("Subject with this code already exists")
        
        subject = models.Subject(
            subject_code=subject_data.subject_code,
            subject_name=subject_data.subject_name,
            faculty_id=subject_data.faculty_id,
            semester=subject_data.semester,
            credits=subject_data.credits,
            department=subject_data.department
        )
        db.add(subject)
        db.commit()
        db.refresh(subject)
        return subject
    
    @staticmethod
    def get_subject_by_id(db: Session, subject_id: int) -> Optional[models.Subject]:
        """Get subject by ID"""
        return db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
    
    @staticmethod
    def get_subject_by_code(db: Session, subject_code: str) -> Optional[models.Subject]:
        """Get subject by code"""
        return db.query(models.Subject).filter(models.Subject.subject_code == subject_code).first()
    
    @staticmethod
    def update_subject(db: Session, subject_id: int, subject_data: schemas.SubjectUpdate) -> models.Subject:
        """Update a subject"""
        subject = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
        
        if not subject:
            raise ValueError("Subject not found")
        
        for key, value in subject_data.dict(exclude_unset=True).items():
            setattr(subject, key, value)
        
        db.commit()
        db.refresh(subject)
        return subject
    
    @staticmethod
    def delete_subject(db: Session, subject_id: int) -> bool:
        """Delete a subject"""
        subject = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
        
        if not subject:
            raise ValueError("Subject not found")
        
        db.delete(subject)
        db.commit()
        return True
    
    @staticmethod
    def get_all_subjects(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        faculty_id: Optional[int] = None
    ) -> List[models.Subject]:
        """Get all subjects with optional filters"""
        query = db.query(models.Subject)
        
        if department:
            query = query.filter(models.Subject.department == department)
        if semester:
            query = query.filter(models.Subject.semester == semester)
        if faculty_id:
            query = query.filter(models.Subject.faculty_id == faculty_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_faculty_subjects(db: Session, faculty_id: int) -> List[models.Subject]:
        """Get all subjects assigned to a faculty member"""
        return db.query(models.Subject).filter(models.Subject.faculty_id == faculty_id).all()
