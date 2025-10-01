# api/routes/student.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from api.middleware.auth import get_db, require_student, require_faculty_or_admin, get_current_user
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.timetable_service import TimetableService
from services.notification_service import NotificationService
import schemas
import models

router = APIRouter(prefix="/api/students", tags=["Students"])

# ========== Student Profile Endpoints ==========

@router.get("/me", response_model=schemas.StudentOut)
def get_my_profile(current_user: models.User = Depends(require_student), db: Session = Depends(get_db)):
    """Get current student's profile"""
    student = StudentService.get_student_by_id(db, current_user.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


@router.put("/me/profile", response_model=schemas.StudentOut)
def update_my_profile(
    profile_data: schemas.StudentProfileUpdate,
    current_user: models.User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Update current student's profile"""
    try:
        student = StudentService.get_student_by_id(db, current_user.user_id)
        if not student:
            # Create profile if doesn't exist
            student = StudentService.create_student_profile(db, current_user.user_id, profile_data)
        else:
            # Update existing profile
            student = StudentService.update_student(db, current_user.user_id, 
                                                   schemas.StudentUpdate(**profile_data.dict()))
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== Student Attendance Endpoints ==========

@router.get("/me/attendance", response_model=List[schemas.AttendanceOut])
def get_my_attendance(
    current_user: models.User = Depends(require_student),
    db: Session = Depends(get_db),
    subject_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get current student's attendance records"""
    student = StudentService.get_student_by_id(db, current_user.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    records = AttendanceService.get_student_attendance(
        db, student.student_id, subject_id, start_date, end_date
    )
    
    # Enrich with additional info
    result = []
    for record in records:
        attendance_dict = {
            "attendance_id": record.attendance_id,
            "student_id": record.student_id,
            "subject_id": record.subject_id,
            "date": record.date,
            "status": record.status,
            "marked_by": record.marked_by,
            "remarks": record.remarks,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "subject_name": record.subject.subject_name if record.subject else None,
            "marked_by_name": record.marked_by_faculty.user.name if record.marked_by_faculty else None
        }
        result.append(schemas.AttendanceOut(**attendance_dict))
    
    return result


@router.get("/me/attendance/stats")
def get_my_attendance_stats(
    current_user: models.User = Depends(require_student),
    db: Session = Depends(get_db),
    subject_id: Optional[int] = Query(None)
):
    """Get current student's attendance statistics"""
    student = StudentService.get_student_by_id(db, current_user.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    stats = AttendanceService.get_attendance_statistics(db, student.student_id, subject_id)
    return stats


# ========== Student Timetable Endpoints ==========

@router.get("/me/timetable", response_model=List[schemas.TimetableOut])
def get_my_timetable(
    current_user: models.User = Depends(require_student),
    db: Session = Depends(get_db),
    day: Optional[str] = Query(None)
):
    """Get current student's timetable"""
    student = StudentService.get_student_by_id(db, current_user.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    timetable = TimetableService.get_student_timetable(db, student.student_id, day)
    
    # Enrich with subject info
    result = []
    for entry in timetable:
        timetable_dict = {
            "timetable_id": entry.timetable_id,
            "subject_id": entry.subject_id,
            "student_id": entry.student_id,
            "day": entry.day,
            "time_slot": entry.time_slot,
            "room_number": entry.room_number,
            "semester": entry.semester,
            "academic_year": entry.academic_year,
            "subject_name": entry.subject.subject_name if entry.subject else None,
            "subject_code": entry.subject.subject_code if entry.subject else None
        }
        result.append(schemas.TimetableOut(**timetable_dict))
    
    return result


# ========== Student Notifications Endpoints ==========

@router.get("/me/notifications", response_model=List[schemas.NotificationOut])
def get_my_notifications(
    current_user: models.User = Depends(require_student),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get notifications for students"""
    notifications = NotificationService.get_notifications_for_role(db, "Student", skip, limit)
    
    # Enrich with creator info
    result = []
    for notif in notifications:
        notif_dict = {
            "notification_id": notif.notification_id,
            "title": notif.title,
            "description": notif.description,
            "created_by": notif.created_by,
            "visible_to": notif.visible_to,
            "priority": notif.priority,
            "is_active": notif.is_active,
            "created_at": notif.created_at,
            "creator_name": notif.creator.user.name if notif.creator else None
        }
        result.append(schemas.NotificationOut(**notif_dict))
    
    return result


# ========== Admin/Faculty: Student Management Endpoints ==========

@router.post("/", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: schemas.StudentCreate,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new student (Faculty/Admin only)"""
    try:
        student = StudentService.create_student(db, student_data)
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.StudentOut])
def get_all_students(
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    class_name: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    section: Optional[str] = Query(None)
):
    """Get all students with filters (Faculty/Admin only)"""
    students = StudentService.get_all_students(db, skip, limit, class_name, year, section)
    return students


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(
    student_id: int,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Get student by ID (Faculty/Admin only)"""
    student = StudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    student_data: schemas.StudentUpdate,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update student profile (Faculty/Admin only)"""
    try:
        student = StudentService.update_student(db, student_id, student_data)
        return student
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Delete student (Faculty/Admin only)"""
    try:
        StudentService.delete_student(db, student_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
