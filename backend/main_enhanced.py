# Enhanced main.py for ERP system
import os
from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
import models, schemas, crud
from deps import (
    get_db, get_current_user, require_role, require_roles, 
    require_permission, get_current_active_user, is_admin_or_faculty, 
    is_admin, get_client_ip
)
from auth import create_access_token
from datetime import timedelta, date
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import csv
import io
import json

load_dotenv()

# create DB tables (only for dev; in prod use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enhanced ERP System API",
    description="Scalable ERP system with role-based access control",
    version="2.0.0"
)

origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative React port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = crud.create_user(db, user_in)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    request: Request = None,
    db: Session = Depends(get_db)
):
    """User login"""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password"
        )
    
    # Create audit log
    if request:
        crud.create_audit_log(
            db, user.user_id, "login", "auth", 
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)))
    token = create_access_token(
        {"user_id": user.user_id, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def verify_token(current_user: models.User = Depends(get_current_active_user)):
    """Verify token and return current user data"""
    return current_user

@app.post("/logout")
def logout(
    current_user: models.User = Depends(get_current_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """User logout"""
    if request:
        crud.create_audit_log(
            db, current_user.user_id, "logout", "auth",
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent")
        )
    return {"message": "Logged out successfully"}

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/users", response_model=List[schemas.UserOut])
def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Get list of users (Admin/Faculty only)"""
    return crud.get_users(db, skip=skip, limit=limit, role=role)

@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin/Faculty only)"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Update user (Admin only)"""
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.create_audit_log(
        db, current_user.user_id, "update", "users", user_id,
        new_values=user_update.dict(exclude_unset=True)
    )
    return user

@app.delete("/users/{user_id}")
def deactivate_user(
    user_id: int,
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Deactivate user (Admin only)"""
    user = crud.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    crud.create_audit_log(
        db, current_user.user_id, "deactivate", "users", user_id
    )
    return {"message": "User deactivated successfully"}

# ============================================================================
# STUDENT ENDPOINTS
# ============================================================================

@app.get("/students", response_model=List[schemas.StudentOut])
def get_students(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Get list of students (Admin/Faculty only)"""
    return crud.get_students(db, skip=skip, limit=limit)

@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(
    student_id: int,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Get student by ID (Admin/Faculty only)"""
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    student_update: schemas.StudentUpdate,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Update student profile (Admin/Faculty only)"""
    student = crud.update_student_profile(db, student_id, student_update)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    crud.create_audit_log(
        db, current_user.user_id, "update", "students", student_id,
        new_values=student_update.dict(exclude_unset=True)
    )
    return student

@app.post("/students/bulk-upload")
def bulk_upload_students(
    file: UploadFile = File(...),
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Bulk upload students from CSV file (Admin/Faculty only)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = file.file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        students_data = list(csv_reader)
        
        created_students = crud.bulk_create_students(db, students_data)
        
        crud.create_audit_log(
            db, current_user.user_id, "bulk_create", "students",
            new_values={"count": len(created_students)}
        )
        
        return {
            "message": f"Successfully created {len(created_students)} students",
            "created_count": len(created_students)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

# Student self-service endpoints
@app.get("/student/profile", response_model=schemas.UserOut)
def get_student_profile(
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Get own profile (Student only)"""
    return current_user

@app.put("/student/profile", response_model=schemas.UserOut)
def update_student_profile_self(
    profile_update: schemas.StudentUpdate,
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Update own profile (Student only)"""
    student = crud.update_student_profile(db, current_user.user_id, profile_update)
    if not student:
        # Create profile if doesn't exist
        student = crud.create_student_profile(db, current_user.user_id, profile_update)
    
    crud.create_audit_log(
        db, current_user.user_id, "update", "profile", current_user.user_id,
        new_values=profile_update.dict(exclude_unset=True)
    )
    return current_user

@app.get("/student/attendance", response_model=List[schemas.AttendanceOut])
def get_student_attendance(
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Get own attendance (Student only)"""
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    records = db.query(models.Attendance).filter(models.Attendance.student_id == student.student_id).all()
    return records

@app.get("/student/grades", response_model=List[schemas.GradeOut])
def get_student_grades(
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Get own grades (Student only)"""
    return crud.get_student_grades(db, current_user.user_id)

@app.get("/student/timetable")
def get_student_timetable(
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Get own timetable (Student only)"""
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    entries = db.query(models.Timetable).filter(models.Timetable.student_id == student.student_id).all()
    return [{
        "class_id": e.class_id,
        "subject_id": e.subject_id,
        "subject_name": e.subject.subject_name if e.subject else None,
        "day": e.day,
        "time_slot": e.time_slot
    } for e in entries]

@app.get("/student/notifications", response_model=List[schemas.NotificationOut])
def get_student_notifications(
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    """Get notifications for students"""
    notifs = db.query(models.Notification).filter(
        (models.Notification.visible_to == "Student") | 
        (models.Notification.visible_to == "All")
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs

# ============================================================================
# FACULTY ENDPOINTS
# ============================================================================

@app.get("/faculty", response_model=List[schemas.FacultyOut])
def get_faculty_list(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Get list of faculty (Admin/Faculty only)"""
    return crud.get_faculty_list(db, skip=skip, limit=limit)

@app.put("/faculty/{faculty_id}", response_model=schemas.FacultyOut)
def update_faculty(
    faculty_id: int,
    faculty_update: schemas.FacultyUpdate,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Update faculty profile"""
    # Faculty can only update their own profile, Admin can update any
    if current_user.role.value == "Faculty" and current_user.user_id != faculty_id:
        raise HTTPException(status_code=403, detail="Can only update own profile")
    
    faculty = crud.update_faculty_profile(db, faculty_id, faculty_update)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    
    crud.create_audit_log(
        db, current_user.user_id, "update", "faculty", faculty_id,
        new_values=faculty_update.dict(exclude_unset=True)
    )
    return faculty

@app.get("/faculty/classes")
def get_faculty_classes(
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Get classes assigned to faculty"""
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    subjects = db.query(models.Subject).filter(models.Subject.faculty_id == faculty.faculty_id).all()
    output = []
    for s in subjects:
        entries = db.query(models.Timetable).filter(models.Timetable.subject_id == s.subject_id).all()
        output.append({
            "subject_id": s.subject_id,
            "subject_name": s.subject_name,
            "subject_code": s.subject_code,
            "semester": s.semester,
            "credits": s.credits,
            "timetable_entries": [{
                "class_id": e.class_id,
                "student_id": e.student_id,
                "day": e.day,
                "time_slot": e.time_slot
            } for e in entries]
        })
    return output

@app.post("/faculty/attendance", response_model=schemas.AttendanceOut)
def mark_attendance(
    att_in: schemas.AttendanceCreate,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Mark student attendance (Faculty only)"""
    # Verify faculty can mark attendance for this subject
    subj = db.query(models.Subject).filter(models.Subject.subject_id == att_in.subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only mark attendance for your subjects")
    
    record = crud.mark_attendance(db, att_in, marked_by=current_user.user_id)
    
    crud.create_audit_log(
        db, current_user.user_id, "mark_attendance", "attendance", record.attendance_id,
        new_values={"student_id": att_in.student_id, "status": att_in.status.value}
    )
    return record

@app.get("/faculty/attendance/{subject_id}", response_model=List[schemas.AttendanceOut])
def get_subject_attendance(
    subject_id: int,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Get attendance for a subject (Faculty only)"""
    subj = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only view attendance for your subjects")
    
    records = db.query(models.Attendance).filter(models.Attendance.subject_id == subject_id).all()
    return records

@app.post("/faculty/grades", response_model=schemas.GradeOut)
def create_grade(
    grade_in: schemas.GradeCreate,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Create grade record (Faculty only)"""
    # Verify faculty can create grades for this subject
    subj = db.query(models.Subject).filter(models.Subject.subject_id == grade_in.subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only create grades for your subjects")
    
    grade = crud.create_grade(db, grade_in)
    
    crud.create_audit_log(
        db, current_user.user_id, "create", "grades", grade.grade_id,
        new_values=grade_in.dict()
    )
    return grade

@app.get("/faculty/grades/{subject_id}", response_model=List[schemas.GradeOut])
def get_subject_grades(
    subject_id: int,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Get grades for a subject (Faculty only)"""
    subj = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only view grades for your subjects")
    
    return crud.get_subject_grades(db, subject_id)

@app.post("/faculty/notifications", response_model=schemas.NotificationOut)
def create_notification(
    notif_in: schemas.NotificationCreate,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Create notification (Faculty only)"""
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    
    notification = crud.create_notification(db, notif_in, faculty.faculty_id)
    
    crud.create_audit_log(
        db, current_user.user_id, "create", "notifications", notification.notification_id,
        new_values=notif_in.dict()
    )
    return notification

@app.get("/faculty/notifications", response_model=List[schemas.NotificationOut])
def get_faculty_notifications(
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    """Get notifications created by faculty"""
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    
    notifs = db.query(models.Notification).filter(
        models.Notification.created_by == faculty.faculty_id
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs

# ============================================================================
# SUBJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/subjects", response_model=List[schemas.SubjectOut])
def get_subjects(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of subjects"""
    return db.query(models.Subject).offset(skip).limit(limit).all()

@app.post("/subjects", response_model=schemas.SubjectOut)
def create_subject(
    subj_in: schemas.SubjectCreate,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Create new subject (Admin/Faculty only)"""
    subject = crud.create_subject(db, subj_in)
    
    crud.create_audit_log(
        db, current_user.user_id, "create", "subjects", subject.subject_id,
        new_values=subj_in.dict()
    )
    return subject

@app.put("/subjects/{subject_id}", response_model=schemas.SubjectOut)
def update_subject(
    subject_id: int,
    subject_update: schemas.SubjectUpdate,
    current_user: models.User = Depends(is_admin_or_faculty),
    db: Session = Depends(get_db)
):
    """Update subject (Admin/Faculty only)"""
    subject = db.query(models.Subject).filter(models.Subject.subject_id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    for key, value in subject_update.dict(exclude_unset=True).items():
        setattr(subject, key, value)
    
    db.commit()
    db.refresh(subject)
    
    crud.create_audit_log(
        db, current_user.user_id, "update", "subjects", subject_id,
        new_values=subject_update.dict(exclude_unset=True)
    )
    return subject

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/admin/dashboard")
def get_admin_dashboard(
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard data"""
    total_users = db.query(models.User).count()
    total_students = db.query(models.Student).count()
    total_faculty = db.query(models.Faculty).count()
    total_subjects = db.query(models.Subject).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_subjects": total_subjects,
        "active_users": active_users,
        "system_health": "Good"
    }

@app.get("/admin/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only)"""
    logs = db.query(models.AuditLog).order_by(
        models.AuditLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    return logs

@app.get("/admin/system-settings", response_model=List[schemas.SystemSettingOut])
def get_system_settings(
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get system settings (Admin only)"""
    return db.query(models.SystemSettings).all()

@app.post("/admin/system-settings", response_model=schemas.SystemSettingOut)
def create_system_setting(
    setting_in: schemas.SystemSettingCreate,
    current_user: models.User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Create/update system setting (Admin only)"""
    setting = crud.set_system_setting(
        db, setting_in.key, setting_in.value, 
        setting_in.description, current_user.user_id
    )
    
    crud.create_audit_log(
        db, current_user.user_id, "set_setting", "system_settings", setting.setting_id,
        new_values=setting_in.dict()
    )
    return setting

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.get("/notifications", response_model=List[schemas.NotificationOut])
def get_notifications(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    role = current_user.role.value
    notifs = db.query(models.Notification).filter(
        (models.Notification.visible_to == role) | 
        (models.Notification.visible_to == "All")
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(models.Notification).filter(
        models.Notification.notification_id == notification_id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ERP System is running"}

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Enhanced ERP System API",
        "version": "2.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)