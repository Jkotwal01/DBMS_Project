from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas, crud
from deps import get_db, require_role

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/attendance", response_model=list[schemas.AttendanceOut])
def student_attendance(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    records = db.query(models.Attendance).filter(models.Attendance.student_id == student.student_id).all()
    return records


@router.get("/timetable")
def student_timetable(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
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


@router.get("/notifications", response_model=list[schemas.NotificationOut])
def student_notifications(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    notifs = db.query(models.Notification).filter(
        (models.Notification.visible_to == "Student") | (models.Notification.visible_to == "All")
    ).order_by(models.Notification.created_at.desc()).all()
    return notifs


@router.get("/profile", response_model=schemas.UserOut)
def student_profile(current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    return current_user


@router.post("/profile")
def complete_student_profile(student_in: schemas.StudentCreate, current_user: models.User = Depends(require_role("Student")), db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.student_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    student = crud.create_student_profile(db, current_user.user_id, student_in)
    return student


@router.put("/profile", response_model=schemas.UserOut)
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

