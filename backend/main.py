# main.py
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
import models, schemas, crud
from deps import get_db, get_current_user, require_role
from auth import create_access_token
from datetime import timedelta
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()



# create DB tables (only for dev; in prod use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Attendance Monitoring API")
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# -- Auth endpoints --
@app.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # create base user
    try:
        user = crud.create_user(db, user_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # create role-specific profile
    if user_in.role == "Student":
        # For simplicity, create with minimal data; client should call profile endpoint to add details
        return user
    elif user_in.role == "Faculty":
        return user
    else:
        return user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    # Generate token payload
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)))
    token = create_access_token({"user_id": user.user_id, "role": user.role.value}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def verify_token(current_user: models.User = Depends(get_current_user)):
    """Verify token and return current user data"""
    return current_user

# -- Student endpoints --
@app.get("/student/attendance", response_model=list[schemas.AttendanceOut])
def student_attendance(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    records = db.query(models.Attendance).filter(models.Attendance.student_id == student.student_id).all()
    return records

@app.get("/student/timetable")
def student_timetable(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    entries = db.query(models.Timetable).filter(models.Timetable.student_id == student.student_id).all()
    # convert to simple dicts for frontend
    return [{
        "class_id": e.class_id,
        "subject_id": e.subject_id,
        "subject_name": e.subject.subject_name if e.subject else None,
        "day": e.day,
        "time_slot": e.time_slot
    } for e in entries]

@app.get("/student/notifications", response_model=list[schemas.NotificationOut])
def student_notifications(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    # students see notifications visible_to=Student or All
    notifs = db.query(models.Notification).filter(
        (models.Notification.visible_to == "Student") | (models.Notification.visible_to == "All")
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs

@app.get("/student/profile", response_model=schemas.UserOut)
def student_profile(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    return current_user

# -- Faculty endpoints --
@app.get("/faculty/classes")
def faculty_classes(current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    subjects = db.query(models.Subject).filter(models.Subject.faculty_id == faculty.faculty_id).all()
    output = []
    for s in subjects:
        # get timetable entries for that subject
        entries = db.query(models.Timetable).filter(models.Timetable.subject_id == s.subject_id).all()
        output.append({
            "subject_id": s.subject_id,
            "subject_name": s.subject_name,
            "semester": s.semester,
            "timetable_entries": [{
                "class_id": e.class_id,
                "student_id": e.student_id,
                "day": e.day,
                "time_slot": e.time_slot
            } for e in entries]
        })
    return output

@app.post("/faculty/attendance", response_model=schemas.AttendanceOut)
def faculty_mark_attendance(att_in: schemas.AttendanceCreate, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    # Only allow marking attendance for subjects that faculty handles
    subj = db.query(models.Subject).filter(models.Subject.subject_id == att_in.subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only mark attendance for your subjects")
    rec = crud.mark_attendance(db, att_in)
    return rec

@app.delete("/faculty/attendance/{attendance_id}")
def faculty_delete_attendance(attendance_id: int, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    att = db.query(models.Attendance).filter(models.Attendance.attendance_id == attendance_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    subj = db.query(models.Subject).filter(models.Subject.subject_id == att.subject_id).first()
    if subj and subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Cannot delete attendance for other faculty's subjects")
    db.delete(att)
    db.commit()
    return {"detail": "deleted"}

@app.post("/faculty/notification", response_model=schemas.NotificationOut)
def faculty_create_notification(notif_in: schemas.NotificationCreate, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    # create notification by this faculty
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    notif = crud.create_notification(db, notif_in, faculty.faculty_id)
    return notif

@app.get("/faculty/notifications")
def faculty_notifications(current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    notifs = db.query(models.Notification).filter(models.Notification.created_by == faculty.faculty_id).order_by(models.Notification.created_at.desc()).all()
    return notifs

# -- Admin-like endpoints for subject creation (for demo) --
@app.post("/subjects", tags=["admin"])
def create_subject(subj_in: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud.create_subject(db, subj_in)

# Utility endpoints to complete profile (student/faculty) after registration:
@app.post("/student/profile")
def complete_student_profile(student_in: schemas.StudentCreate, current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    student = crud.create_student_profile(db, current_user.user_id, student_in)
    return student

@app.post("/faculty/profile")
def complete_faculty_profile(fac_in: schemas.FacultyCreate, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    existing = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    faculty = crud.create_faculty_profile(db, current_user.user_id, fac_in)
    return faculty

@app.put("/student/profile", response_model=schemas.UserOut)
def update_student_profile(
    profile_update: schemas.StudentCreate,
    current_user: models.User = Depends(require_role("Student")),
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        student = crud.create_student_profile(db, current_user.user_id, profile_update)
    else:
        for key, value in profile_update.dict(exclude_unset=True).items():
            setattr(student, key, value)
        db.commit()
    return current_user

@app.put("/faculty/profile", response_model=schemas.UserOut)
def update_faculty_profile(
    profile_update: schemas.FacultyCreate,
    current_user: models.User = Depends(require_role("Faculty")),
    db: Session = Depends(get_db)
):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        faculty = crud.create_faculty_profile(db, current_user.user_id, profile_update)
    else:
        for key, value in profile_update.dict(exclude_unset=True).items():
            setattr(faculty, key, value)
        db.commit()
    return current_user
