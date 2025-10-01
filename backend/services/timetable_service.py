# services/timetable_service.py
from sqlalchemy.orm import Session
from typing import Optional, List
import models, schemas

class TimetableService:
    """Service layer for timetable-related operations"""
    
    @staticmethod
    def create_timetable_entry(db: Session, timetable_data: schemas.TimetableCreate) -> models.Timetable:
        """Create a timetable entry for a student"""
        # Check for conflicts
        conflict = db.query(models.Timetable).filter(
            models.Timetable.student_id == timetable_data.student_id,
            models.Timetable.day == timetable_data.day,
            models.Timetable.time_slot == timetable_data.time_slot
        ).first()
        
        if conflict:
            raise ValueError("Time slot already occupied for this student")
        
        timetable = models.Timetable(
            subject_id=timetable_data.subject_id,
            student_id=timetable_data.student_id,
            day=timetable_data.day,
            time_slot=timetable_data.time_slot,
            room_number=timetable_data.room_number,
            semester=timetable_data.semester,
            academic_year=timetable_data.academic_year
        )
        db.add(timetable)
        db.commit()
        db.refresh(timetable)
        return timetable
    
    @staticmethod
    def bulk_create_timetable(
        db: Session, 
        timetable_data: schemas.TimetableBulkCreate
    ) -> dict:
        """Create timetable entries for multiple students"""
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, student_id in enumerate(timetable_data.student_ids):
            try:
                entry_data = schemas.TimetableCreate(
                    subject_id=timetable_data.subject_id,
                    student_id=student_id,
                    day=timetable_data.day,
                    time_slot=timetable_data.time_slot,
                    room_number=timetable_data.room_number,
                    semester=timetable_data.semester,
                    academic_year=timetable_data.academic_year
                )
                TimetableService.create_timetable_entry(db, entry_data)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({
                    'student_id': student_id,
                    'error': str(e)
                })
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors,
            'message': f'Successfully created {success_count} timetable entries. {error_count} errors.'
        }
    
    @staticmethod
    def get_student_timetable(
        db: Session, 
        student_id: int,
        day: Optional[str] = None
    ) -> List[models.Timetable]:
        """Get timetable for a student"""
        query = db.query(models.Timetable).filter(models.Timetable.student_id == student_id)
        
        if day:
            query = query.filter(models.Timetable.day == day)
        
        return query.all()
    
    @staticmethod
    def get_subject_timetable(
        db: Session, 
        subject_id: int
    ) -> List[models.Timetable]:
        """Get all timetable entries for a subject"""
        return db.query(models.Timetable).filter(
            models.Timetable.subject_id == subject_id
        ).all()
    
    @staticmethod
    def update_timetable_entry(
        db: Session, 
        timetable_id: int, 
        timetable_data: schemas.TimetableUpdate
    ) -> models.Timetable:
        """Update a timetable entry"""
        timetable = db.query(models.Timetable).filter(
            models.Timetable.timetable_id == timetable_id
        ).first()
        
        if not timetable:
            raise ValueError("Timetable entry not found")
        
        # Check for conflicts if day or time is being updated
        if timetable_data.day or timetable_data.time_slot:
            new_day = timetable_data.day or timetable.day
            new_time = timetable_data.time_slot or timetable.time_slot
            
            conflict = db.query(models.Timetable).filter(
                models.Timetable.student_id == timetable.student_id,
                models.Timetable.day == new_day,
                models.Timetable.time_slot == new_time,
                models.Timetable.timetable_id != timetable_id
            ).first()
            
            if conflict:
                raise ValueError("Time slot already occupied for this student")
        
        for key, value in timetable_data.dict(exclude_unset=True).items():
            setattr(timetable, key, value)
        
        db.commit()
        db.refresh(timetable)
        return timetable
    
    @staticmethod
    def delete_timetable_entry(db: Session, timetable_id: int) -> bool:
        """Delete a timetable entry"""
        timetable = db.query(models.Timetable).filter(
            models.Timetable.timetable_id == timetable_id
        ).first()
        
        if not timetable:
            raise ValueError("Timetable entry not found")
        
        db.delete(timetable)
        db.commit()
        return True
    
    @staticmethod
    def delete_student_timetable(db: Session, student_id: int) -> bool:
        """Delete all timetable entries for a student"""
        db.query(models.Timetable).filter(
            models.Timetable.student_id == student_id
        ).delete()
        db.commit()
        return True
