# services/attendance_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import models, schemas

class AttendanceService:
    """Service layer for attendance-related operations"""
    
    @staticmethod
    def mark_attendance(
        db: Session, 
        attendance_data: schemas.AttendanceCreate, 
        faculty_id: int
    ) -> models.Attendance:
        """Mark attendance for a student"""
        # Check if attendance already exists
        existing = db.query(models.Attendance).filter(
            models.Attendance.student_id == attendance_data.student_id,
            models.Attendance.subject_id == attendance_data.subject_id,
            models.Attendance.date == attendance_data.date
        ).first()
        
        if existing:
            # Update existing record
            existing.status = attendance_data.status
            existing.marked_by = faculty_id
            existing.remarks = attendance_data.remarks
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new attendance record
        attendance = models.Attendance(
            student_id=attendance_data.student_id,
            subject_id=attendance_data.subject_id,
            date=attendance_data.date,
            status=attendance_data.status,
            marked_by=faculty_id,
            remarks=attendance_data.remarks
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance
    
    @staticmethod
    def bulk_mark_attendance(
        db: Session, 
        subject_id: int, 
        date_val: date, 
        attendance_list: List[dict],
        faculty_id: int
    ) -> dict:
        """Bulk mark attendance for multiple students"""
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, att_dict in enumerate(attendance_list):
            try:
                attendance_data = schemas.AttendanceCreate(
                    student_id=att_dict['student_id'],
                    subject_id=subject_id,
                    date=date_val,
                    status=att_dict['status'],
                    remarks=att_dict.get('remarks')
                )
                AttendanceService.mark_attendance(db, attendance_data, faculty_id)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({
                    'row': idx + 1,
                    'student_id': att_dict.get('student_id'),
                    'error': str(e)
                })
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors,
            'message': f'Successfully marked attendance for {success_count} students. {error_count} errors.'
        }
    
    @staticmethod
    def get_student_attendance(
        db: Session, 
        student_id: int,
        subject_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[models.Attendance]:
        """Get attendance records for a student"""
        query = db.query(models.Attendance).filter(models.Attendance.student_id == student_id)
        
        if subject_id:
            query = query.filter(models.Attendance.subject_id == subject_id)
        if start_date:
            query = query.filter(models.Attendance.date >= start_date)
        if end_date:
            query = query.filter(models.Attendance.date <= end_date)
        
        return query.order_by(models.Attendance.date.desc()).all()
    
    @staticmethod
    def get_subject_attendance(
        db: Session, 
        subject_id: int,
        date_val: Optional[date] = None
    ) -> List[models.Attendance]:
        """Get attendance records for a subject"""
        query = db.query(models.Attendance).filter(models.Attendance.subject_id == subject_id)
        
        if date_val:
            query = query.filter(models.Attendance.date == date_val)
        
        return query.order_by(models.Attendance.date.desc()).all()
    
    @staticmethod
    def update_attendance(
        db: Session, 
        attendance_id: int, 
        attendance_data: schemas.AttendanceUpdate
    ) -> models.Attendance:
        """Update an attendance record"""
        attendance = db.query(models.Attendance).filter(
            models.Attendance.attendance_id == attendance_id
        ).first()
        
        if not attendance:
            raise ValueError("Attendance record not found")
        
        for key, value in attendance_data.dict(exclude_unset=True).items():
            setattr(attendance, key, value)
        
        db.commit()
        db.refresh(attendance)
        return attendance
    
    @staticmethod
    def delete_attendance(db: Session, attendance_id: int) -> bool:
        """Delete an attendance record"""
        attendance = db.query(models.Attendance).filter(
            models.Attendance.attendance_id == attendance_id
        ).first()
        
        if not attendance:
            raise ValueError("Attendance record not found")
        
        db.delete(attendance)
        db.commit()
        return True
    
    @staticmethod
    def get_attendance_statistics(db: Session, student_id: int, subject_id: Optional[int] = None) -> dict:
        """Get attendance statistics for a student"""
        query = db.query(models.Attendance).filter(models.Attendance.student_id == student_id)
        
        if subject_id:
            query = query.filter(models.Attendance.subject_id == subject_id)
        
        records = query.all()
        total = len(records)
        present = len([r for r in records if r.status == 'Present'])
        absent = len([r for r in records if r.status == 'Absent'])
        late = len([r for r in records if r.status == 'Late'])
        excused = len([r for r in records if r.status == 'Excused'])
        
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'total_classes': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_percentage': round(percentage, 2)
        }
