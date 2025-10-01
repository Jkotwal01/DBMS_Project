# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# ============= Auth Schemas =============
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

# ============= User Schemas =============
class UserBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ============= Student Schemas =============
class StudentBase(BaseModel):
    roll_no: str
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    division: Optional[str] = None
    batch: Optional[str] = None
    admission_date: Optional[date] = None

class StudentCreate(StudentBase):
    user: UserCreate

class StudentUpdate(BaseModel):
    roll_no: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    division: Optional[str] = None
    batch: Optional[str] = None
    admission_date: Optional[date] = None

class StudentProfileUpdate(StudentBase):
    pass

class StudentOut(BaseModel):
    student_id: int
    roll_no: str
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    division: Optional[str] = None
    batch: Optional[str] = None
    admission_date: Optional[date] = None
    user: UserOut

    class Config:
        from_attributes = True

# ============= Faculty Schemas =============
class FacultyBase(BaseModel):
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    dept: Optional[str] = None
    specialization: Optional[str] = None
    joining_date: Optional[date] = None

class FacultyCreate(FacultyBase):
    user: UserCreate

class FacultyUpdate(BaseModel):
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    dept: Optional[str] = None
    specialization: Optional[str] = None
    joining_date: Optional[date] = None

class FacultyProfileUpdate(FacultyBase):
    pass

class FacultyOut(BaseModel):
    faculty_id: int
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    dept: Optional[str] = None
    specialization: Optional[str] = None
    joining_date: Optional[date] = None
    user: UserOut

    class Config:
        from_attributes = True

# ============= Subject Schemas =============
class SubjectBase(BaseModel):
    subject_code: Optional[str] = None
    subject_name: str
    semester: Optional[int] = None
    credits: Optional[int] = 3
    department: Optional[str] = None

class SubjectCreate(SubjectBase):
    faculty_id: Optional[int] = None

class SubjectUpdate(BaseModel):
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    credits: Optional[int] = None
    department: Optional[str] = None

class SubjectOut(BaseModel):
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: str
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    credits: int
    department: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ============= Timetable Schemas =============
class TimetableBase(BaseModel):
    subject_id: int
    day: str
    time_slot: str
    room_number: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None

class TimetableCreate(TimetableBase):
    student_id: int

class TimetableBulkCreate(BaseModel):
    subject_id: int
    day: str
    time_slot: str
    room_number: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    student_ids: List[int]  # For bulk creation

class TimetableUpdate(BaseModel):
    subject_id: Optional[int] = None
    day: Optional[str] = None
    time_slot: Optional[str] = None
    room_number: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None

class TimetableOut(BaseModel):
    timetable_id: int
    subject_id: int
    student_id: int
    day: str
    time_slot: str
    room_number: Optional[str] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None

    class Config:
        from_attributes = True

# ============= Attendance Schemas =============
class AttendanceBase(BaseModel):
    student_id: int
    subject_id: int
    date: date
    status: str = Field(..., pattern="^(Present|Absent|Late|Excused)$")
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceBulkCreate(BaseModel):
    subject_id: int
    date: date
    attendance_list: List[dict]  # [{"student_id": 1, "status": "Present"}, ...]

class AttendanceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Present|Absent|Late|Excused)$")
    remarks: Optional[str] = None

class AttendanceOut(BaseModel):
    attendance_id: int
    student_id: int
    subject_id: int
    date: date
    status: str
    marked_by: Optional[int] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Additional info for display
    student_name: Optional[str] = None
    subject_name: Optional[str] = None
    marked_by_name: Optional[str] = None

    class Config:
        from_attributes = True

# ============= Notification Schemas =============
class NotificationBase(BaseModel):
    title: str
    description: str
    visible_to: str = "Student"
    priority: str = "normal"

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visible_to: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None

class NotificationOut(BaseModel):
    notification_id: int
    title: str
    description: str
    created_by: int
    visible_to: str
    priority: str
    is_active: bool
    created_at: datetime
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True

# ============= Bulk Upload Schemas =============
class BulkStudentUpload(BaseModel):
    students: List[dict]  # List of student data dictionaries

class BulkUploadResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[dict] = []
    message: str
