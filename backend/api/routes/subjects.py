# api/routes/subjects.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from api.middleware.auth import get_db, require_faculty_or_admin, get_current_user
from services.subject_service import SubjectService
import schemas
import models

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])

@router.post("/", response_model=schemas.SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: schemas.SubjectCreate,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new subject (Faculty/Admin only)"""
    try:
        subject = SubjectService.create_subject(db, subject_data)
        return subject
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.SubjectOut])
def get_all_subjects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    faculty_id: Optional[int] = Query(None)
):
    """Get all subjects with optional filters"""
    subjects = SubjectService.get_all_subjects(db, skip, limit, department, semester, faculty_id)
    return subjects


@router.get("/{subject_id}", response_model=schemas.SubjectOut)
def get_subject(
    subject_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get subject by ID"""
    subject = SubjectService.get_subject_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/{subject_id}", response_model=schemas.SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: schemas.SubjectUpdate,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Update a subject (Faculty/Admin only)"""
    try:
        subject = SubjectService.update_subject(db, subject_id, subject_data)
        return subject
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    current_user: models.User = Depends(require_faculty_or_admin),
    db: Session = Depends(get_db)
):
    """Delete a subject (Faculty/Admin only)"""
    try:
        SubjectService.delete_subject(db, subject_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
