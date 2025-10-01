from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
from io import StringIO

import models, schemas, crud
from deps import get_db, require_role

router = APIRouter(prefix="/faculty", tags=["faculty"])


@router.get("/classes")
def faculty_classes(current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
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
            "semester": s.semester,
            "timetable_entries": [{
                "class_id": e.class_id,
                "student_id": e.student_id,
                "day": e.day,
                "time_slot": e.time_slot
            } for e in entries]
        })
    return output


@router.post("/attendance", response_model=schemas.AttendanceOut)
def faculty_mark_attendance(att_in: schemas.AttendanceCreate, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    subj = db.query(models.Subject).filter(models.Subject.subject_id == att_in.subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    if subj.faculty_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only mark attendance for your subjects")
    rec = crud.mark_attendance(db, att_in, marked_by=current_user.user_id)
    return rec


@router.delete("/attendance/{attendance_id}")
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


@router.post("/notification", response_model=schemas.NotificationOut)
def faculty_create_notification(notif_in: schemas.NotificationCreate, current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    notif = crud.create_notification(db, notif_in, faculty.faculty_id)
    return notif


@router.get("/notifications")
def faculty_notifications(current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == current_user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile missing")
    notifs = db.query(models.Notification).filter(models.Notification.created_by == faculty.faculty_id).order_by(models.Notification.created_at.desc()).all()
    return notifs


@router.post("/students/upload")
async def upload_students_csv(file: UploadFile = File(...), current_user: models.User = Depends(require_role("Faculty")), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    created = 0
    for row in reader:
        # Expect columns: name,email,roll_no,class_name,year,section
        user_in = schemas.UserCreate(name=row["name"], email=row["email"], password=row.get("password", "changeme123"), role="Student")
        try:
            user = crud.create_user(db, user_in)
        except Exception:
            continue
        student_in = schemas.StudentCreate(
            roll_no=row["roll_no"],
            class_name=row.get("class_name"),
            year=int(row.get("year")) if row.get("year") else None,
            section=row.get("section")
        )
        crud.create_student_profile(db, user.user_id, student_in)
        created += 1
    return {"created": created}

