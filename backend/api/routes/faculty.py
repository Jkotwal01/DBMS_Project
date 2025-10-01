# api/routes/faculty.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from api.middleware.auth import get_db, require_faculty, require_faculty_or_admin, get_current_user
from services.faculty_service import FacultyService
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.timetable_service import TimetableService
from services.notification_service import NotificationService
from services.subject_service import SubjectService
from utils.csv_processor import CSVProcessor
import schemas
import models

router = APIRouter(prefix="/api/faculty", tags=["Faculty"])

# ========== Faculty Profile Endpoints ==========

@router.get("/me", response_model=schemas.FacultyOut)
def get_my_profile(current_user: models.User = Depends(require_faculty), db: Session = Depends(get_db)):
    """Get current faculty's profile"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    return faculty


@router.put("/me/profile", response_model=schemas.FacultyOut)
def update_my_profile(
    profile_data: schemas.FacultyProfileUpdate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Update current faculty's profile"""
    try:
        faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
        if not faculty:
            # Create profile if doesn't exist
            faculty = FacultyService.create_faculty_profile(db, current_user.user_id, profile_data)
        else:
            # Update existing profile
            faculty = FacultyService.update_faculty(db, current_user.user_id, 
                                                   schemas.FacultyUpdate(**profile_data.dict()))
        return faculty
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/subjects", response_model=List[schemas.SubjectOut])
def get_my_subjects(current_user: models.User = Depends(require_faculty), db: Session = Depends(get_db)):
    """Get subjects assigned to current faculty"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    subjects = SubjectService.get_faculty_subjects(db, faculty.faculty_id)
    return subjects


# ========== Faculty Attendance Management ==========

@router.post("/attendance", response_model=schemas.AttendanceOut, status_code=status.HTTP_201_CREATED)
def mark_attendance(
    attendance_data: schemas.AttendanceCreate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Mark attendance for a student"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Verify faculty teaches this subject
    subject = SubjectService.get_subject_by_id(db, attendance_data.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only mark attendance for your subjects")
    
    try:
        attendance = AttendanceService.mark_attendance(db, attendance_data, faculty.faculty_id)
        
        # Enrich response
        attendance_dict = {
            "attendance_id": attendance.attendance_id,
            "student_id": attendance.student_id,
            "subject_id": attendance.subject_id,
            "date": attendance.date,
            "status": attendance.status,
            "marked_by": attendance.marked_by,
            "remarks": attendance.remarks,
            "created_at": attendance.created_at,
            "updated_at": attendance.updated_at,
            "student_name": attendance.student.user.name if attendance.student else None,
            "subject_name": attendance.subject.subject_name if attendance.subject else None,
            "marked_by_name": current_user.name
        }
        return schemas.AttendanceOut(**attendance_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/attendance/bulk")
def bulk_mark_attendance(
    bulk_data: schemas.AttendanceBulkCreate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Mark attendance for multiple students"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Verify faculty teaches this subject
    subject = SubjectService.get_subject_by_id(db, bulk_data.subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only mark attendance for your subjects")
    
    result = AttendanceService.bulk_mark_attendance(
        db, bulk_data.subject_id, bulk_data.date, bulk_data.attendance_list, faculty.faculty_id
    )
    return result


@router.get("/attendance/subject/{subject_id}")
def get_subject_attendance(
    subject_id: int,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db),
    date_val: Optional[str] = Query(None)
):
    """Get attendance records for a subject"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Verify faculty teaches this subject
    subject = SubjectService.get_subject_by_id(db, subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only view attendance for your subjects")
    
    from datetime import datetime
    date_obj = datetime.strptime(date_val, "%Y-%m-%d").date() if date_val else None
    
    records = AttendanceService.get_subject_attendance(db, subject_id, date_obj)
    return records


@router.delete("/attendance/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    attendance_id: int,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Delete an attendance record"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Get attendance record
    attendance = db.query(models.Attendance).filter(
        models.Attendance.attendance_id == attendance_id
    ).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Verify faculty owns this record
    subject = SubjectService.get_subject_by_id(db, attendance.subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only delete your own attendance records")
    
    try:
        AttendanceService.delete_attendance(db, attendance_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Faculty Timetable Management ==========

@router.post("/timetable", response_model=schemas.TimetableOut, status_code=status.HTTP_201_CREATED)
def create_timetable_entry(
    timetable_data: schemas.TimetableCreate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Create a timetable entry"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Verify faculty teaches this subject
    subject = SubjectService.get_subject_by_id(db, timetable_data.subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only create timetable for your subjects")
    
    try:
        timetable = TimetableService.create_timetable_entry(db, timetable_data)
        
        # Enrich response
        timetable_dict = {
            "timetable_id": timetable.timetable_id,
            "subject_id": timetable.subject_id,
            "student_id": timetable.student_id,
            "day": timetable.day,
            "time_slot": timetable.time_slot,
            "room_number": timetable.room_number,
            "semester": timetable.semester,
            "academic_year": timetable.academic_year,
            "subject_name": timetable.subject.subject_name if timetable.subject else None,
            "subject_code": timetable.subject.subject_code if timetable.subject else None
        }
        return schemas.TimetableOut(**timetable_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/timetable/bulk")
def bulk_create_timetable(
    bulk_data: schemas.TimetableBulkCreate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Create timetable entries for multiple students"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Verify faculty teaches this subject
    subject = SubjectService.get_subject_by_id(db, bulk_data.subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only create timetable for your subjects")
    
    result = TimetableService.bulk_create_timetable(db, bulk_data)
    return result


@router.delete("/timetable/{timetable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable_entry(
    timetable_id: int,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Delete a timetable entry"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Get timetable entry
    timetable = db.query(models.Timetable).filter(
        models.Timetable.timetable_id == timetable_id
    ).first()
    
    if not timetable:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    
    # Verify faculty owns this entry
    subject = SubjectService.get_subject_by_id(db, timetable.subject_id)
    if not subject or subject.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only delete your own timetable entries")
    
    try:
        TimetableService.delete_timetable_entry(db, timetable_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Faculty Notification Management ==========

@router.post("/notifications", response_model=schemas.NotificationOut, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: schemas.NotificationCreate,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Create a notification"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    notification = NotificationService.create_notification(db, notification_data, faculty.faculty_id)
    
    # Enrich response
    notif_dict = {
        "notification_id": notification.notification_id,
        "title": notification.title,
        "description": notification.description,
        "created_by": notification.created_by,
        "visible_to": notification.visible_to,
        "priority": notification.priority,
        "is_active": notification.is_active,
        "created_at": notification.created_at,
        "creator_name": current_user.name
    }
    return schemas.NotificationOut(**notif_dict)


@router.get("/notifications", response_model=List[schemas.NotificationOut])
def get_my_notifications(
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get notifications created by current faculty"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    notifications = NotificationService.get_faculty_notifications(db, faculty.faculty_id, skip, limit)
    
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
            "creator_name": current_user.name
        }
        result.append(schemas.NotificationOut(**notif_dict))
    
    return result


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: models.User = Depends(require_faculty),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    faculty = FacultyService.get_faculty_by_id(db, current_user.user_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    
    # Get notification
    notification = NotificationService.get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Verify faculty owns this notification
    if notification.created_by != faculty.faculty_id:
        raise HTTPException(status_code=403, detail="You can only delete your own notifications")
    
    try:
        NotificationService.delete_notification(db, notification_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ========== Bulk Student Upload ==========

@router.post("/students/bulk-upload")
async def bulk_upload_students(
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """
    Upload students in bulk via CSV file.
    CSV should have columns: name, email, roll_no, class_name, year, section, division, department, phone
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Parse CSV
        students_data = await CSVProcessor.parse_student_csv(file)
        
        if not students_data:
            raise HTTPException(status_code=400, detail="No valid student data found in CSV")
        
        # Bulk create students
        result = StudentService.bulk_create_students(db, students_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")


@router.get("/students/csv-template")
def get_csv_template():
    """Get a sample CSV template for student upload"""
    template = CSVProcessor.generate_sample_student_csv()
    return {"template": template}


# ========== Faculty CRUD (Admin only) ==========

@router.post("/", response_model=schemas.FacultyOut, status_code=status.HTTP_201_CREATED)
def create_faculty(
    faculty_data: schemas.FacultyCreate,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new faculty (Admin only)"""
    try:
        faculty = FacultyService.create_faculty(db, faculty_data)
        return faculty
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.FacultyOut])
def get_all_faculty(
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    dept: Optional[str] = Query(None)
):
    """Get all faculty members"""
    faculty_list = FacultyService.get_all_faculty(db, skip, limit, dept)
    return faculty_list


@router.get("/{faculty_id}", response_model=schemas.FacultyOut)
def get_faculty(
    faculty_id: int,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Get faculty by ID"""
    faculty = FacultyService.get_faculty_by_id(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty
