# services/student_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas
from services.user_service import UserService

class StudentService:
    """Service layer for student-related operations"""
    
    @staticmethod
    def create_student(db: Session, student_data: schemas.StudentCreate) -> models.Student:
        """Create a new student with user account"""
        # Create user first
        user = UserService.create_user(db, student_data.user)
        
        # Create student profile
        student = models.Student(
            student_id=user.user_id,
            roll_no=student_data.roll_no,
            class_name=student_data.class_name,
            year=student_data.year,
            section=student_data.section,
            division=student_data.division,
            batch=student_data.batch,
            admission_date=student_data.admission_date
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Optional[models.Student]:
        """Get student by ID with user details"""
        return db.query(models.Student).filter(models.Student.student_id == student_id).first()
    
    @staticmethod
    def get_student_by_roll_no(db: Session, roll_no: str) -> Optional[models.Student]:
        """Get student by roll number"""
        return db.query(models.Student).filter(models.Student.roll_no == roll_no).first()
    
    @staticmethod
    def update_student(db: Session, student_id: int, student_data: schemas.StudentUpdate) -> models.Student:
        """Update student profile"""
        student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        
        for key, value in student_data.dict(exclude_unset=True).items():
            setattr(student, key, value)
        
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        """Delete student and associated user account"""
        student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        
        # Delete user (cascade will delete student)
        return UserService.delete_user(db, student_id)
    
    @staticmethod
    def get_all_students(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        class_name: Optional[str] = None,
        year: Optional[int] = None,
        section: Optional[str] = None
    ) -> List[models.Student]:
        """Get all students with optional filters"""
        query = db.query(models.Student)
        
        if class_name:
            query = query.filter(models.Student.class_name == class_name)
        if year:
            query = query.filter(models.Student.year == year)
        if section:
            query = query.filter(models.Student.section == section)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_student_profile(db: Session, user_id: int, profile_data: schemas.StudentProfileUpdate) -> models.Student:
        """Create student profile for existing user"""
        student = models.Student(
            student_id=user_id,
            roll_no=profile_data.roll_no,
            class_name=profile_data.class_name,
            year=profile_data.year,
            section=profile_data.section,
            division=profile_data.division,
            batch=profile_data.batch,
            admission_date=profile_data.admission_date
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def bulk_create_students(db: Session, students_data: List[dict]) -> dict:
        """Bulk create students from list of dictionaries"""
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, student_dict in enumerate(students_data):
            try:
                # Validate and create student
                user_data = schemas.UserCreate(
                    name=student_dict.get('name'),
                    email=student_dict.get('email'),
                    password=student_dict.get('password', 'student123'),  # Default password
                    role='Student',
                    department=student_dict.get('department'),
                    phone=student_dict.get('phone'),
                    address=student_dict.get('address')
                )
                
                student_create = schemas.StudentCreate(
                    user=user_data,
                    roll_no=student_dict.get('roll_no'),
                    class_name=student_dict.get('class_name'),
                    year=student_dict.get('year'),
                    section=student_dict.get('section'),
                    division=student_dict.get('division'),
                    batch=student_dict.get('batch')
                )
                
                StudentService.create_student(db, student_create)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({
                    'row': idx + 1,
                    'data': student_dict,
                    'error': str(e)
                })
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors,
            'message': f'Successfully created {success_count} students. {error_count} errors.'
        }
