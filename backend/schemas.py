# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int]
    role: Optional[str]

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    department: Optional[str] = None

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    department: Optional[str] = None

    class Config:
        orm_mode = True

class StudentCreate(BaseModel):
    roll_no: str
    class_name: Optional[str]
    year: Optional[int]
    section: Optional[str]

class FacultyCreate(BaseModel):
    designation: Optional[str]
    dept: Optional[str]

class SubjectCreate(BaseModel):
    subject_name: str
    faculty_id: Optional[int] = None
    semester: Optional[int] = None

class TimetableCreate(BaseModel):
    subject_id: int
    student_id: int
    day: str
    time_slot: str
    room: str | None = None
    class_name: str | None = None

class AttendanceCreate(BaseModel):
    student_id: int
    subject_id: int
    date: date
    status: str
    marked_by: int | None = None

class NotificationCreate(BaseModel):
    title: str
    description: str
    visible_to: str = "Student"  # deprecated in favor of receiver_role
    receiver_role: str | None = "Student"

class NotificationOut(BaseModel):
    notification_id: int
    title: str
    description: str
    created_by: int
    visible_to: str
    receiver_role: str | None
    created_at: datetime

    class Config:
        orm_mode = True

class AttendanceOut(BaseModel):
    attendance_id: int
    student_id: int
    subject_id: int
    date: date
    status: str

    class Config:
        orm_mode = True
