# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class RoleEnum(str, Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"

class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"

class NotificationPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

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
    role: RoleEnum
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class StudentCreate(BaseModel):
    roll_no: str
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    admission_date: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

class StudentUpdate(BaseModel):
    roll_no: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

class StudentOut(BaseModel):
    student_id: int
    roll_no: str
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    admission_date: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    class Config:
        orm_mode = True

class FacultyCreate(BaseModel):
    designation: Optional[str] = None
    dept: Optional[str] = None
    employee_id: Optional[str] = None
    joining_date: Optional[date] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    salary: Optional[int] = None

class FacultyUpdate(BaseModel):
    designation: Optional[str] = None
    dept: Optional[str] = None
    employee_id: Optional[str] = None
    joining_date: Optional[date] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    salary: Optional[int] = None

class FacultyOut(BaseModel):
    faculty_id: int
    designation: Optional[str] = None
    dept: Optional[str] = None
    employee_id: Optional[str] = None
    joining_date: Optional[date] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None

    class Config:
        orm_mode = True

class SubjectCreate(BaseModel):
    subject_name: str
    subject_code: Optional[str] = None
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    credits: Optional[int] = 3
    description: Optional[str] = None

class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    credits: Optional[int] = None
    description: Optional[str] = None

class SubjectOut(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: Optional[str] = None
    faculty_id: Optional[int] = None
    semester: Optional[int] = None
    credits: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class TimetableCreate(BaseModel):
    subject_id: int
    student_id: int
    day: str
    time_slot: str

class TimetableOut(BaseModel):
    class_id: int
    subject_id: int
    student_id: int
    day: str
    time_slot: str

    class Config:
        orm_mode = True

class AttendanceCreate(BaseModel):
    student_id: int
    subject_id: int
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None

class AttendanceOut(BaseModel):
    attendance_id: int
    student_id: int
    subject_id: int
    date: date
    status: str
    marked_by: Optional[int] = None
    marked_at: datetime
    remarks: Optional[str] = None

    class Config:
        orm_mode = True

class NotificationCreate(BaseModel):
    title: str
    description: str
    visible_to: str = "Student"
    priority: NotificationPriority = NotificationPriority.MEDIUM
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visible_to: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    is_read: Optional[bool] = None
    expires_at: Optional[datetime] = None

class NotificationOut(BaseModel):
    notification_id: int
    title: str
    description: str
    created_by: int
    visible_to: str
    priority: str
    is_read: bool
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

# New schemas for enhanced ERP features

class AdminCreate(BaseModel):
    employee_id: Optional[str] = None
    access_level: int = 1

class AdminOut(BaseModel):
    admin_id: int
    employee_id: Optional[str] = None
    access_level: int

    class Config:
        orm_mode = True

class ParentCreate(BaseModel):
    occupation: Optional[str] = None
    annual_income: Optional[int] = None

class ParentOut(BaseModel):
    parent_id: int
    occupation: Optional[str] = None
    annual_income: Optional[int] = None

    class Config:
        orm_mode = True

class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    exam_type: str
    marks_obtained: int
    total_marks: int
    grade_letter: Optional[str] = None
    exam_date: date

class GradeUpdate(BaseModel):
    marks_obtained: Optional[int] = None
    total_marks: Optional[int] = None
    grade_letter: Optional[str] = None
    exam_date: Optional[date] = None

class GradeOut(BaseModel):
    grade_id: int
    student_id: int
    subject_id: int
    exam_type: str
    marks_obtained: int
    total_marks: int
    grade_letter: Optional[str] = None
    exam_date: date
    created_at: datetime

    class Config:
        orm_mode = True

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionOut(BaseModel):
    permission_id: int
    name: str
    description: Optional[str] = None
    resource: str
    action: str

    class Config:
        orm_mode = True

class BulkStudentUpload(BaseModel):
    students: List[dict]

class SystemSettingCreate(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettingOut(BaseModel):
    setting_id: int
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: datetime

    class Config:
        orm_mode = True
