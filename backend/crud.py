# crud.py
from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password, verify_password, create_access_token
from datetime import timedelta

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
        department=user_in.department
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # if student or faculty, we must create associated record; caller should pass student/faculty info
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
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

def mark_attendance(db: Session, att_in: schemas.AttendanceCreate):
    # try to update existing or insert new
    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == att_in.student_id,
        models.Attendance.subject_id == att_in.subject_id,
        models.Attendance.date == att_in.date
    ).first()
    if existing:
        existing.status = att_in.status
        db.commit()
        db.refresh(existing)
        return existing
    att = models.Attendance(
        student_id=att_in.student_id,
        subject_id=att_in.subject_id,
        date=att_in.date,
        status=att_in.status
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
        visible_to=notif_in.visible_to
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
