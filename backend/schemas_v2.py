# schemas_v2.py - Enhanced Pydantic Schemas for ERP System
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class RoleEnum(str, Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"

class StatusEnum(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    GRADUATED = "Graduated"

class AttendanceStatusEnum(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"

class NotificationTypeEnum(str, Enum):
    GENERAL = "General"
    ATTENDANCE = "Attendance"
    ACADEMIC = "Academic"
    ADMINISTRATIVE = "Administrative"
    EMERGENCY = "Emergency"

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_role: str

class TokenData(BaseModel):
    user_id: Optional[int]
    role: Optional[str]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: RoleEnum
    department: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[StatusEnum] = None

class UserOut(UserBase):
    user_id: int
    role: RoleEnum
    department: Optional[str] = None
    status: StatusEnum
    profile_picture: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

# Department Schemas
class DepartmentBase(BaseModel):
    dept_name: str
    dept_code: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    head_faculty_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    dept_name: Optional[str] = None
    dept_code: Optional[str] = None
    description: Optional[str] = None
    head_faculty_id: Optional[int] = None

class DepartmentOut(DepartmentBase):
    dept_id: int
    head_faculty_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Academic Year & Semester Schemas
class AcademicYearBase(BaseModel):
    year_name: str
    start_date: date
    end_date: date

class AcademicYearCreate(AcademicYearBase):
    is_current: bool = False

class AcademicYearOut(AcademicYearBase):
    year_id: int
    is_current: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SemesterBase(BaseModel):
    semester_name: str
    start_date: date
    end_date: date

class SemesterCreate(SemesterBase):
    academic_year_id: int
    is_current: bool = False

class SemesterOut(SemesterBase):
    semester_id: int
    academic_year_id: int
    is_current: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Student Schemas
class StudentBase(BaseModel):
    roll_no: str
    student_id_number: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    batch: Optional[str] = None
    enrollment_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class StudentCreate(StudentBase):
    dept_id: Optional[int] = None
    current_semester_id: Optional[int] = None

class StudentUpdate(BaseModel):
    roll_no: Optional[str] = None
    student_id_number: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    batch: Optional[str] = None
    dept_id: Optional[int] = None
    current_semester_id: Optional[int] = None
    enrollment_date: Optional[date] = None
    gpa: Optional[float] = None
    total_credits: Optional[int] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class StudentOut(StudentBase):
    student_id: int
    dept_id: Optional[int] = None
    current_semester_id: Optional[int] = None
    gpa: Optional[float] = None
    total_credits: int

    class Config:
        from_attributes = True

class StudentWithUser(StudentOut):
    user: UserOut

# Faculty Schemas
class FacultyBase(BaseModel):
    employee_id: str
    designation: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    joining_date: Optional[date] = None

class FacultyCreate(FacultyBase):
    dept_id: Optional[int] = None

class FacultyUpdate(BaseModel):
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    dept_id: Optional[int] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    joining_date: Optional[date] = None
    is_head: Optional[bool] = None

class FacultyOut(FacultyBase):
    faculty_id: int
    dept_id: Optional[int] = None
    is_head: bool

    class Config:
        from_attributes = True

class FacultyWithUser(FacultyOut):
    user: UserOut

# Subject Schemas
class SubjectBase(BaseModel):
    subject_code: str
    subject_name: str
    credits: Optional[int] = None
    semester: Optional[int] = None
    description: Optional[str] = None
    is_elective: bool = False

class SubjectCreate(SubjectBase):
    faculty_id: Optional[int] = None
    dept_id: Optional[int] = None

class SubjectUpdate(BaseModel):
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    faculty_id: Optional[int] = None
    dept_id: Optional[int] = None
    credits: Optional[int] = None
    semester: Optional[int] = None
    description: Optional[str] = None
    is_elective: Optional[bool] = None

class SubjectOut(SubjectBase):
    subject_id: int
    faculty_id: Optional[int] = None
    dept_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Timetable Schemas
class TimetableBase(BaseModel):
    class_room: Optional[str] = None
    day: str
    start_time: str
    end_time: str
    is_active: bool = True

class TimetableCreate(TimetableBase):
    subject_id: int
    faculty_id: int
    semester_id: int

class TimetableUpdate(BaseModel):
    subject_id: Optional[int] = None
    faculty_id: Optional[int] = None
    class_room: Optional[str] = None
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    semester_id: Optional[int] = None
    is_active: Optional[bool] = None

class TimetableOut(TimetableBase):
    timetable_id: int
    subject_id: int
    faculty_id: int
    semester_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TimetableWithDetails(TimetableOut):
    subject: SubjectOut
    faculty: FacultyWithUser

# Attendance Schemas
class AttendanceSessionBase(BaseModel):
    session_date: date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    notes: Optional[str] = None

class AttendanceSessionCreate(AttendanceSessionBase):
    timetable_id: int

class AttendanceSessionOut(AttendanceSessionBase):
    session_id: int
    timetable_id: int
    is_completed: bool
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    status: AttendanceStatusEnum
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    session_id: int
    student_id: int

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatusEnum] = None
    remarks: Optional[str] = None

class AttendanceOut(AttendanceBase):
    attendance_id: int
    session_id: int
    student_id: int
    marked_at: datetime
    marked_by: Optional[int] = None

    class Config:
        from_attributes = True

class AttendanceWithDetails(AttendanceOut):
    student: StudentWithUser
    session: AttendanceSessionOut

# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationTypeEnum = NotificationTypeEnum.GENERAL
    is_urgent: bool = False
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    receiver_id: Optional[int] = None
    target_role: Optional[RoleEnum] = None
    target_department: Optional[int] = None
    is_broadcast: bool = False

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[NotificationTypeEnum] = None
    is_urgent: Optional[bool] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationOut(NotificationBase):
    notification_id: int
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    created_by: Optional[int] = None
    target_role: Optional[RoleEnum] = None
    target_department: Optional[int] = None
    is_broadcast: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Enrollment Schemas
class EnrollmentBase(BaseModel):
    enrollment_date: date
    status: str = "Enrolled"

class EnrollmentCreate(EnrollmentBase):
    student_id: int
    subject_id: int
    semester_id: int

class EnrollmentUpdate(BaseModel):
    grade: Optional[str] = None
    credits_earned: Optional[int] = None
    status: Optional[str] = None

class EnrollmentOut(EnrollmentBase):
    enrollment_id: int
    student_id: int
    subject_id: int
    semester_id: int
    grade: Optional[str] = None
    credits_earned: Optional[int] = None

    class Config:
        from_attributes = True

# Bulk Upload Schemas
class BulkUploadResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]
    message: str

class StudentBulkUpload(BaseModel):
    name: str
    email: EmailStr
    roll_no: str
    class_name: Optional[str] = None
    year: Optional[int] = None
    section: Optional[str] = None
    batch: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class FacultyBulkUpload(BaseModel):
    name: str
    email: EmailStr
    employee_id: str
    designation: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_students: int
    total_faculty: int
    total_departments: int
    total_subjects: int
    active_sessions: int
    pending_notifications: int

class StudentDashboard(BaseModel):
    user: UserOut
    student: StudentOut
    attendance_summary: Dict[str, Any]
    recent_notifications: List[NotificationOut]
    upcoming_classes: List[TimetableWithDetails]

class FacultyDashboard(BaseModel):
    user: UserOut
    faculty: FacultyOut
    assigned_subjects: List[SubjectOut]
    recent_attendance: List[AttendanceWithDetails]
    pending_notifications: List[NotificationOut]

# File Upload Schemas
class FileUploadBase(BaseModel):
    purpose: str
    description: Optional[str] = None

class FileUploadOut(BaseModel):
    file_id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    purpose: str
    is_processed: bool
    upload_date: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogOut(BaseModel):
    audit_id: int
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Login Log Schemas
class LoginLogOut(BaseModel):
    log_id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_time: datetime
    logout_time: Optional[datetime] = None
    is_successful: bool
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True