# crud.py
from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password, verify_password, create_access_token
from datetime import timedelta, datetime
from typing import List, Optional
import json

def create_user(db: Session, user_in: schemas.UserCreate):
    # check existing
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise Exception("User with this email already exists")
    hashed = hash_password(user_in.password)
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed,
        role=user_in.role,
        department=user_in.department,
        phone=user_in.phone,
        address=user_in.address
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        return None
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100, role: Optional[str] = None):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.offset(skip).limit(limit).all()

def deactivate_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    return user

# Student / Faculty creation convenience
def create_student_profile(db: Session, user_id: int, student_in: schemas.StudentCreate):
    student = models.Student(
        student_id=user_id,
        roll_no=student_in.roll_no,
        class_name=student_in.class_name,
        year=student_in.year,
        section=student_in.section
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def create_faculty_profile(db: Session, user_id: int, fac_in: schemas.FacultyCreate):
    fac = models.Faculty(
        faculty_id=user_id,
        designation=fac_in.designation,
        dept=fac_in.dept
    )
    db.add(fac)
    db.commit()
    db.refresh(fac)
    return fac

# Subject CRUD
def create_subject(db: Session, subj_in: schemas.SubjectCreate):
    subj = models.Subject(
        subject_name=subj_in.subject_name,
        faculty_id=subj_in.faculty_id,
        semester=subj_in.semester
    )
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj

# Timetable & Attendance & Notification
def add_timetable_entry(db: Session, tt_in: schemas.TimetableCreate):
    entry = models.Timetable(
        subject_id=tt_in.subject_id,
        student_id=tt_in.student_id,
        day=tt_in.day,
        time_slot=tt_in.time_slot
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def mark_attendance(db: Session, att_in: schemas.AttendanceCreate, marked_by: Optional[int] = None):
    # try to update existing or insert new
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == att_in.student_id,
        models.Attendance.subject_id == att_in.subject_id,
        models.Attendance.date == att_in.date
    ).first()
    if existing:
        existing.status = att_in.status
        existing.remarks = att_in.remarks
        existing.marked_by = marked_by
        existing.marked_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    att = models.Attendance(
        student_id=att_in.student_id,
        subject_id=att_in.subject_id,
        date=att_in.date,
        status=att_in.status,
        remarks=att_in.remarks,
        marked_by=marked_by
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att

def create_notification(db: Session, notif_in: schemas.NotificationCreate, faculty_id: int):
    notif = models.Notification(
        title=notif_in.title,
        description=notif_in.description,
        created_by=faculty_id,
        visible_to=notif_in.visible_to,
        priority=notif_in.priority,
        expires_at=notif_in.expires_at
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

# Enhanced CRUD operations for new ERP features

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).join(models.User).offset(skip).limit(limit).all()

def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()

def update_student_profile(db: Session, student_id: int, student_update: schemas.StudentUpdate):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        return None
    
    for key, value in student_update.dict(exclude_unset=True).items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    return student

def get_faculty_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Faculty).join(models.User).offset(skip).limit(limit).all()

def update_faculty_profile(db: Session, faculty_id: int, faculty_update: schemas.FacultyUpdate):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_id).first()
    if not faculty:
        return None
    
    for key, value in faculty_update.dict(exclude_unset=True).items():
        setattr(faculty, key, value)
    
    db.commit()
    db.refresh(faculty)
    return faculty

def create_grade(db: Session, grade_in: schemas.GradeCreate):
    grade = models.Grade(
        student_id=grade_in.student_id,
        subject_id=grade_in.subject_id,
        exam_type=grade_in.exam_type,
        marks_obtained=grade_in.marks_obtained,
        total_marks=grade_in.total_marks,
        grade_letter=grade_in.grade_letter,
        exam_date=grade_in.exam_date
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

def get_student_grades(db: Session, student_id: int):
    return db.query(models.Grade).filter(models.Grade.student_id == student_id).all()

def get_subject_grades(db: Session, subject_id: int):
    return db.query(models.Grade).filter(models.Grade.subject_id == subject_id).all()

def create_permission(db: Session, permission_in: schemas.PermissionCreate):
    permission = models.Permission(
        name=permission_in.name,
        description=permission_in.description,
        resource=permission_in.resource,
        action=permission_in.action
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission

def get_permissions(db: Session):
    return db.query(models.Permission).all()

def assign_permission_to_user(db: Session, user_id: int, permission_id: int, granted_by: int):
    user_permission = models.UserPermission(
        user_id=user_id,
        permission_id=permission_id,
        granted_by=granted_by
    )
    db.add(user_permission)
    db.commit()
    db.refresh(user_permission)
    return user_permission

def get_user_permissions(db: Session, user_id: int):
    return db.query(models.UserPermission).filter(models.UserPermission.user_id == user_id).all()

def bulk_create_students(db: Session, students_data: List[dict]):
    created_students = []
    for student_data in students_data:
        try:
            # Create user first
            user_data = {
                "name": student_data["name"],
                "email": student_data["email"],
                "password": student_data.get("password", "defaultpass123"),
                "role": "Student",
                "department": student_data.get("department"),
                "phone": student_data.get("phone"),
                "address": student_data.get("address")
            }
            user = create_user(db, schemas.UserCreate(**user_data))
            
            # Create student profile
            student_profile_data = {
                "roll_no": student_data["roll_no"],
                "class_name": student_data.get("class_name"),
                "year": student_data.get("year"),
                "section": student_data.get("section"),
                "admission_date": student_data.get("admission_date"),
                "guardian_name": student_data.get("guardian_name"),
                "guardian_phone": student_data.get("guardian_phone"),
                "blood_group": student_data.get("blood_group"),
                "date_of_birth": student_data.get("date_of_birth"),
                "gender": student_data.get("gender")
            }
            student = create_student_profile(db, user.user_id, schemas.StudentCreate(**student_profile_data))
            created_students.append(student)
        except Exception as e:
            # Log error but continue with other students
            print(f"Error creating student {student_data.get('name', 'Unknown')}: {str(e)}")
            continue
    
    return created_students

def create_audit_log(db: Session, user_id: int, action: str, resource: str, resource_id: Optional[int] = None, 
                    old_values: Optional[dict] = None, new_values: Optional[dict] = None, 
                    ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    audit_log = models.AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

def get_system_setting(db: Session, key: str):
    return db.query(models.SystemSettings).filter(models.SystemSettings.key == key).first()

def set_system_setting(db: Session, key: str, value: str, description: Optional[str] = None, updated_by: Optional[int] = None):
    setting = get_system_setting(db, key)
    if setting:
        setting.value = value
        setting.description = description
        setting.updated_by = updated_by
        setting.updated_at = datetime.utcnow()
    else:
        setting = models.SystemSettings(
            key=key,
            value=value,
            description=description,
            updated_by=updated_by
        )
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting
