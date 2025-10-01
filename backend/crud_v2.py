# crud_v2.py - Enhanced CRUD Operations with Clean Architecture
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import models_v2 as models
import schemas_v2 as schemas
from auth import hash_password, verify_password
import json

# Base CRUD Operations
class BaseCRUD:
    def __init__(self, model):
        self.model = model
    
    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: schemas.BaseModel):
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj, obj_in: schemas.BaseModel):
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int):
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# User Management
class UserCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.User)
    
    def get_by_email(self, db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()
    
    def get_by_id(self, db: Session, user_id: int):
        return db.query(models.User).filter(models.User.user_id == user_id).first()
    
    def create_user(self, db: Session, user_in: schemas.UserCreate):
        # Check if user already exists
        existing = self.get_by_email(db, user_in.email)
        if existing:
            raise ValueError("User with this email already exists")
        
        hashed_password = hash_password(user_in.password)
        user_data = user_in.dict(exclude={'password'})
        user_data['password_hash'] = hashed_password
        
        user = models.User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate_user(self, db: Session, email: str, password: str):
        user = self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def update_last_login(self, db: Session, user_id: int):
        user = self.get_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    def get_users_by_role(self, db: Session, role: models.RoleEnum, skip: int = 0, limit: int = 100):
        return db.query(models.User).filter(
            models.User.role == role
        ).offset(skip).limit(limit).all()
    
    def get_users_by_department(self, db: Session, dept_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.User).join(models.Student).filter(
            models.Student.dept_id == dept_id
        ).union(
            db.query(models.User).join(models.Faculty).filter(
                models.Faculty.dept_id == dept_id
            )
        ).offset(skip).limit(limit).all()

# Student Management
class StudentCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Student)
    
    def get_by_roll_no(self, db: Session, roll_no: str):
        return db.query(models.Student).filter(models.Student.roll_no == roll_no).first()
    
    def get_with_user(self, db: Session, student_id: int):
        return db.query(models.Student).options(
            joinedload(models.Student.user)
        ).filter(models.Student.student_id == student_id).first()
    
    def create_student_profile(self, db: Session, user_id: int, student_in: schemas.StudentCreate):
        # Check if roll number already exists
        existing = self.get_by_roll_no(db, student_in.roll_no)
        if existing:
            raise ValueError("Student with this roll number already exists")
        
        student_data = student_in.dict()
        student_data['student_id'] = user_id
        
        student = models.Student(**student_data)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    def get_students_by_department(self, db: Session, dept_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Student).options(
            joinedload(models.Student.user)
        ).filter(
            models.Student.dept_id == dept_id
        ).offset(skip).limit(limit).all()
    
    def get_students_by_class(self, db: Session, class_name: str, section: str = None, skip: int = 0, limit: int = 100):
        query = db.query(models.Student).options(
            joinedload(models.Student.user)
        ).filter(models.Student.class_name == class_name)
        
        if section:
            query = query.filter(models.Student.section == section)
        
        return query.offset(skip).limit(limit).all()
    
    def get_attendance_summary(self, db: Session, student_id: int, start_date: date = None, end_date: date = None):
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        attendance_records = db.query(models.Attendance).join(models.AttendanceSession).filter(
            models.Attendance.student_id == student_id,
            models.AttendanceSession.session_date >= start_date,
            models.AttendanceSession.session_date <= end_date
        ).all()
        
        total_sessions = len(attendance_records)
        present_count = sum(1 for record in attendance_records if record.status == models.AttendanceStatusEnum.PRESENT)
        attendance_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'present_count': present_count,
            'absent_count': total_sessions - present_count,
            'attendance_percentage': round(attendance_percentage, 2)
        }

# Faculty Management
class FacultyCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Faculty)
    
    def get_by_employee_id(self, db: Session, employee_id: str):
        return db.query(models.Faculty).filter(models.Faculty.employee_id == employee_id).first()
    
    def get_with_user(self, db: Session, faculty_id: int):
        return db.query(models.Faculty).options(
            joinedload(models.Faculty.user)
        ).filter(models.Faculty.faculty_id == faculty_id).first()
    
    def create_faculty_profile(self, db: Session, user_id: int, faculty_in: schemas.FacultyCreate):
        # Check if employee ID already exists
        existing = self.get_by_employee_id(db, faculty_in.employee_id)
        if existing:
            raise ValueError("Faculty with this employee ID already exists")
        
        faculty_data = faculty_in.dict()
        faculty_data['faculty_id'] = user_id
        
        faculty = models.Faculty(**faculty_data)
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
        return faculty
    
    def get_faculty_by_department(self, db: Session, dept_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Faculty).options(
            joinedload(models.Faculty.user)
        ).filter(
            models.Faculty.dept_id == dept_id
        ).offset(skip).limit(limit).all()
    
    def get_faculty_subjects(self, db: Session, faculty_id: int):
        return db.query(models.Subject).options(
            joinedload(models.Subject.department)
        ).filter(models.Subject.faculty_id == faculty_id).all()

# Department Management
class DepartmentCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Department)
    
    def get_by_code(self, db: Session, dept_code: str):
        return db.query(models.Department).filter(models.Department.dept_code == dept_code).first()
    
    def get_with_head_faculty(self, db: Session, dept_id: int):
        return db.query(models.Department).options(
            joinedload(models.Department.head_faculty).joinedload(models.Faculty.user)
        ).filter(models.Department.dept_id == dept_id).first()

# Subject Management
class SubjectCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Subject)
    
    def get_by_code(self, db: Session, subject_code: str):
        return db.query(models.Subject).filter(models.Subject.subject_code == subject_code).first()
    
    def get_with_faculty(self, db: Session, subject_id: int):
        return db.query(models.Subject).options(
            joinedload(models.Subject.faculty).joinedload(models.Faculty.user),
            joinedload(models.Subject.department)
        ).filter(models.Subject.subject_id == subject_id).first()
    
    def get_subjects_by_department(self, db: Session, dept_id: int, skip: int = 0, limit: int = 100):
        return db.query(models.Subject).options(
            joinedload(models.Subject.faculty).joinedload(models.Faculty.user)
        ).filter(
            models.Subject.dept_id == dept_id
        ).offset(skip).limit(limit).all()
    
    def get_subjects_by_faculty(self, db: Session, faculty_id: int):
        return db.query(models.Subject).options(
            joinedload(models.Subject.department)
        ).filter(models.Subject.faculty_id == faculty_id).all()

# Attendance Management
class AttendanceCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Attendance)
    
    def mark_attendance(self, db: Session, attendance_in: schemas.AttendanceCreate, marked_by: int):
        # Check if attendance already exists for this session and student
        existing = db.query(models.Attendance).filter(
            models.Attendance.session_id == attendance_in.session_id,
            models.Attendance.student_id == attendance_in.student_id
        ).first()
        
        if existing:
            # Update existing record
            existing.status = attendance_in.status
            existing.remarks = attendance_in.remarks
            existing.marked_by = marked_by
            existing.marked_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new record
        attendance_data = attendance_in.dict()
        attendance_data['marked_by'] = marked_by
        
        attendance = models.Attendance(**attendance_data)
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance
    
    def get_attendance_by_session(self, db: Session, session_id: int):
        return db.query(models.Attendance).options(
            joinedload(models.Attendance.student).joinedload(models.Student.user)
        ).filter(models.Attendance.session_id == session_id).all()
    
    def get_student_attendance(self, db: Session, student_id: int, start_date: date = None, end_date: date = None):
        query = db.query(models.Attendance).join(models.AttendanceSession).options(
            joinedload(models.Attendance.session).joinedload(models.AttendanceSession.timetable)
        ).filter(models.Attendance.student_id == student_id)
        
        if start_date:
            query = query.filter(models.AttendanceSession.session_date >= start_date)
        if end_date:
            query = query.filter(models.AttendanceSession.session_date <= end_date)
        
        return query.order_by(desc(models.AttendanceSession.session_date)).all()
    
    def bulk_mark_attendance(self, db: Session, session_id: int, attendance_data: List[Dict[str, Any]], marked_by: int):
        results = []
        for data in attendance_data:
            try:
                attendance = schemas.AttendanceCreate(
                    session_id=session_id,
                    student_id=data['student_id'],
                    status=data['status'],
                    remarks=data.get('remarks')
                )
                result = self.mark_attendance(db, attendance, marked_by)
                results.append({'success': True, 'data': result})
            except Exception as e:
                results.append({'success': False, 'error': str(e), 'data': data})
        return results

# Notification Management
class NotificationCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Notification)
    
    def create_notification(self, db: Session, notification_in: schemas.NotificationCreate, sender_id: int):
        notification_data = notification_in.dict()
        notification_data['sender_id'] = sender_id
        
        notification = models.Notification(**notification_data)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    def get_notifications_for_user(self, db: Session, user_id: int, role: models.RoleEnum, skip: int = 0, limit: int = 50):
        # Get personal notifications
        personal_notifs = db.query(models.Notification).filter(
            models.Notification.receiver_id == user_id
        )
        
        # Get role-based notifications
        role_notifs = db.query(models.Notification).filter(
            models.Notification.target_role == role,
            models.Notification.is_broadcast == True
        )
        
        # Get broadcast notifications
        broadcast_notifs = db.query(models.Notification).filter(
            models.Notification.is_broadcast == True,
            models.Notification.target_role.is_(None)
        )
        
        # Combine and order by creation date
        all_notifications = personal_notifs.union(role_notifs).union(broadcast_notifs).order_by(
            desc(models.Notification.created_at)
        ).offset(skip).limit(limit).all()
        
        return all_notifications
    
    def get_notifications_by_faculty(self, db: Session, faculty_id: int, skip: int = 0, limit: int = 50):
        return db.query(models.Notification).filter(
            models.Notification.created_by == faculty_id
        ).order_by(desc(models.Notification.created_at)).offset(skip).limit(limit).all()

# Timetable Management
class TimetableCRUD(BaseCRUD):
    def __init__(self):
        super().__init__(models.Timetable)
    
    def get_timetable_for_student(self, db: Session, student_id: int, semester_id: int = None):
        # Get student's enrolled subjects
        enrollments = db.query(models.Enrollment).filter(
            models.Enrollment.student_id == student_id
        )
        
        if semester_id:
            enrollments = enrollments.filter(models.Enrollment.semester_id == semester_id)
        
        subject_ids = [e.subject_id for e in enrollments.all()]
        
        # Get timetable for those subjects
        return db.query(models.Timetable).options(
            joinedload(models.Timetable.subject),
            joinedload(models.Timetable.faculty).joinedload(models.Faculty.user)
        ).filter(
            models.Timetable.subject_id.in_(subject_ids),
            models.Timetable.is_active == True
        ).all()
    
    def get_timetable_for_faculty(self, db: Session, faculty_id: int, semester_id: int = None):
        query = db.query(models.Timetable).options(
            joinedload(models.Timetable.subject),
            joinedload(models.Timetable.semester)
        ).filter(
            models.Timetable.faculty_id == faculty_id,
            models.Timetable.is_active == True
        )
        
        if semester_id:
            query = query.filter(models.Timetable.semester_id == semester_id)
        
        return query.all()
    
    def create_timetable_entry(self, db: Session, timetable_in: schemas.TimetableCreate):
        timetable_data = timetable_in.dict()
        timetable = models.Timetable(**timetable_data)
        db.add(timetable)
        db.commit()
        db.refresh(timetable)
        return timetable

# Bulk Upload Operations
class BulkUploadCRUD:
    def bulk_create_students(self, db: Session, students_data: List[schemas.StudentBulkUpload], created_by: int):
        results = {'success': [], 'errors': []}
        
        for i, student_data in enumerate(students_data):
            try:
                # Create user first
                user_data = schemas.UserCreate(
                    name=student_data.name,
                    email=student_data.email,
                    password="temp_password_123",  # Will be changed on first login
                    role=models.RoleEnum.STUDENT,
                    phone=student_data.phone
                )
                
                user_crud = UserCRUD()
                user = user_crud.create_user(db, user_data)
                
                # Create student profile
                student_profile = schemas.StudentCreate(
                    roll_no=student_data.roll_no,
                    class_name=student_data.class_name,
                    year=student_data.year,
                    section=student_data.section,
                    batch=student_data.batch,
                    enrollment_date=date.today(),
                    emergency_contact=student_data.emergency_contact,
                    emergency_phone=student_data.emergency_phone
                )
                
                # Find department if specified
                if student_data.department:
                    dept_crud = DepartmentCRUD()
                    dept = dept_crud.get_by_code(db, student_data.department)
                    if dept:
                        student_profile.dept_id = dept.dept_id
                
                student_crud = StudentCRUD()
                student = student_crud.create_student_profile(db, user.user_id, student_profile)
                
                results['success'].append({
                    'row': i + 1,
                    'user_id': user.user_id,
                    'student_id': student.student_id,
                    'name': student_data.name,
                    'roll_no': student_data.roll_no
                })
                
            except Exception as e:
                results['errors'].append({
                    'row': i + 1,
                    'error': str(e),
                    'data': student_data.dict()
                })
        
        return results
    
    def bulk_create_faculty(self, db: Session, faculty_data: List[schemas.FacultyBulkUpload], created_by: int):
        results = {'success': [], 'errors': []}
        
        for i, faculty_info in enumerate(faculty_data):
            try:
                # Create user first
                user_data = schemas.UserCreate(
                    name=faculty_info.name,
                    email=faculty_info.email,
                    password="temp_password_123",  # Will be changed on first login
                    role=models.RoleEnum.FACULTY,
                    phone=faculty_info.phone
                )
                
                user_crud = UserCRUD()
                user = user_crud.create_user(db, user_data)
                
                # Create faculty profile
                faculty_profile = schemas.FacultyCreate(
                    employee_id=faculty_info.employee_id,
                    designation=faculty_info.designation,
                    joining_date=date.today()
                )
                
                # Find department if specified
                if faculty_info.department:
                    dept_crud = DepartmentCRUD()
                    dept = dept_crud.get_by_code(db, faculty_info.department)
                    if dept:
                        faculty_profile.dept_id = dept.dept_id
                
                faculty_crud = FacultyCRUD()
                faculty = faculty_crud.create_faculty_profile(db, user.user_id, faculty_profile)
                
                results['success'].append({
                    'row': i + 1,
                    'user_id': user.user_id,
                    'faculty_id': faculty.faculty_id,
                    'name': faculty_info.name,
                    'employee_id': faculty_info.employee_id
                })
                
            except Exception as e:
                results['errors'].append({
                    'row': i + 1,
                    'error': str(e),
                    'data': faculty_info.dict()
                })
        
        return results

# Initialize CRUD instances
user_crud = UserCRUD()
student_crud = StudentCRUD()
faculty_crud = FacultyCRUD()
department_crud = DepartmentCRUD()
subject_crud = SubjectCRUD()
attendance_crud = AttendanceCRUD()
notification_crud = NotificationCRUD()
timetable_crud = TimetableCRUD()
bulk_upload_crud = BulkUploadCRUD()