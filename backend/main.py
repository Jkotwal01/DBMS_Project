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
from routers import auth as auth_router
from routers import student as student_router
from routers import faculty as faculty_router

load_dotenv()



# create DB tables (only for dev; in prod use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ERP API")
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

app.include_router(auth_router.router)

app.include_router(student_router.router)

app.include_router(faculty_router.router)

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
