# models_v2.py - Enhanced ERP Database Schema
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Text, TIMESTAMP, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from database import Base
import enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import LONGTEXT

class RoleEnum(str, enum.Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"

class StatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    GRADUATED = "Graduated"

class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"

class NotificationTypeEnum(str, enum.Enum):
    GENERAL = "General"
    ATTENDANCE = "Attendance"
    ACADEMIC = "Academic"
    ADMINISTRATIVE = "Administrative"
    EMERGENCY = "Emergency"

# Core User Management
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE)
    profile_picture = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete")
    faculty = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete")
    admin = relationship("Admin", uselist=False, back_populates="user", cascade="all, delete")
    parent = relationship("Parent", uselist=False, back_populates="user", cascade="all, delete")
    
    # Activity tracking
    login_logs = relationship("LoginLog", back_populates="user", cascade="all, delete")
    notifications_sent = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")
    notifications_received = relationship("Notification", foreign_keys="Notification.receiver_id", back_populates="receiver")

# Department Management
class Department(Base):
    __tablename__ = "departments"
    
    dept_id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String(100), unique=True, nullable=False)
    dept_code = Column(String(10), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    head_faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    head_faculty = relationship("Faculty", foreign_keys=[head_faculty_id])
    students = relationship("Student", back_populates="department")
    faculty_members = relationship("Faculty", back_populates="department")
    subjects = relationship("Subject", back_populates="department")

# Academic Management
class AcademicYear(Base):
    __tablename__ = "academic_years"
    
    year_id = Column(Integer, primary_key=True, index=True)
    year_name = Column(String(50), unique=True, nullable=False)  # e.g., "2024-2025"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Semester(Base):
    __tablename__ = "semesters"
    
    semester_id = Column(Integer, primary_key=True, index=True)
    semester_name = Column(String(50), nullable=False)  # e.g., "Fall 2024", "Spring 2025"
    academic_year_id = Column(Integer, ForeignKey("academic_years.year_id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    academic_year = relationship("AcademicYear")
    students = relationship("Student", back_populates="current_semester")

# Student Management
class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    roll_no = Column(String(50), unique=True, nullable=False)
    student_id_number = Column(String(50), unique=True, nullable=True)  # University ID
    class_name = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    section = Column(String(10), nullable=True)
    batch = Column(String(20), nullable=True)  # e.g., "2024"
    dept_id = Column(Integer, ForeignKey("departments.dept_id", ondelete="SET NULL"), nullable=True)
    current_semester_id = Column(Integer, ForeignKey("semesters.semester_id", ondelete="SET NULL"), nullable=True)
    enrollment_date = Column(Date, nullable=True)
    gpa = Column(Float, nullable=True)
    total_credits = Column(Integer, default=0)
    emergency_contact = Column(String(100), nullable=True)
    emergency_phone = Column(String(20), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    current_semester = relationship("Semester", back_populates="students")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="student", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete")
    parent_relations = relationship("ParentStudent", back_populates="student", cascade="all, delete")

# Faculty Management
class Faculty(Base):
    __tablename__ = "faculty"
    
    faculty_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    designation = Column(String(50), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.dept_id", ondelete="SET NULL"), nullable=True)
    qualification = Column(Text, nullable=True)
    specialization = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    joining_date = Column(Date, nullable=True)
    salary = Column(Float, nullable=True)
    is_head = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="faculty")
    department = relationship("Department", back_populates="faculty_members")
    subjects = relationship("Subject", back_populates="faculty", cascade="all, delete")
    notifications_sent = relationship("Notification", foreign_keys="Notification.created_by", back_populates="creator", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="faculty", cascade="all, delete")

# Admin Management
class Admin(Base):
    __tablename__ = "admins"
    
    admin_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    designation = Column(String(50), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.dept_id", ondelete="SET NULL"), nullable=True)
    permissions = Column(JSON, nullable=True)  # Store permission array
    joining_date = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="admin")
    department = relationship("Department")

# Parent Management
class Parent(Base):
    __tablename__ = "parents"
    
    parent_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    occupation = Column(String(100), nullable=True)
    workplace = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="parent")
    student_relations = relationship("ParentStudent", back_populates="parent", cascade="all, delete")

class ParentStudent(Base):
    __tablename__ = "parent_students"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(20), nullable=False)  # Father, Mother, Guardian
    is_primary = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    parent_rel = relationship("Parent", back_populates="student_relations")
    student_rel = relationship("Student", back_populates="parent_relations")

# Subject Management
class Subject(Base):
    __tablename__ = "subjects"
    
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(20), unique=True, nullable=False)
    subject_name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.dept_id", ondelete="SET NULL"), nullable=True)
    credits = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_elective = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    faculty = relationship("Faculty", back_populates="subjects")
    department = relationship("Department", back_populates="subjects")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="subject", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="subject", cascade="all, delete")

# Enrollment Management
class Enrollment(Base):
    __tablename__ = "enrollments"
    
    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(Date, nullable=False)
    grade = Column(String(5), nullable=True)  # A, B, C, D, F
    credits_earned = Column(Integer, nullable=True)
    status = Column(String(20), default="Enrolled")  # Enrolled, Completed, Dropped
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")
    semester = relationship("Semester")

# Timetable Management
class Timetable(Base):
    __tablename__ = "timetable"
    
    timetable_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="CASCADE"), nullable=False)
    class_room = Column(String(50), nullable=True)
    day = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String(10), nullable=False)  # HH:MM format
    end_time = Column(String(10), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.semester_id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="timetable_entries")
    faculty = relationship("Faculty", back_populates="timetable_entries")
    semester = relationship("Semester")
    attendance_sessions = relationship("AttendanceSession", back_populates="timetable", cascade="all, delete")

# Attendance Management
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    timetable_id = Column(Integer, ForeignKey("timetable.timetable_id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)
    end_time = Column(String(10), nullable=True)
    is_completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    timetable = relationship("Timetable", back_populates="attendance_sessions")
    creator = relationship("Faculty")
    attendance_records = relationship("Attendance", back_populates="session", cascade="all, delete")

class Attendance(Base):
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.session_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)
    remarks = Column(Text, nullable=True)
    marked_at = Column(TIMESTAMP, server_default=func.now())
    marked_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    session = relationship("AttendanceSession", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")
    marker = relationship("Faculty")
    
    # Unique constraint to prevent duplicate attendance for same session
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )

# Notification System
class Notification(Base):
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    message = Column(LONGTEXT, nullable=False)
    notification_type = Column(Enum(NotificationTypeEnum), default=NotificationTypeEnum.GENERAL)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    created_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="CASCADE"), nullable=True)
    target_role = Column(Enum(RoleEnum), nullable=True)  # For role-based notifications
    target_department = Column(Integer, ForeignKey("departments.dept_id", ondelete="SET NULL"), nullable=True)
    is_broadcast = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    scheduled_for = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="notifications_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="notifications_received")
    creator = relationship("Faculty", foreign_keys=[created_by], back_populates="notifications_sent")
    department = relationship("Department")

# System Logs
class LoginLog(Base):
    __tablename__ = "login_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    login_time = Column(TIMESTAMP, server_default=func.now())
    logout_time = Column(TIMESTAMP, nullable=True)
    is_successful = Column(Boolean, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="login_logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    audit_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    user = relationship("User")

# File Management
class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    file_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    purpose = Column(String(50), nullable=True)  # profile, document, bulk_upload, etc.
    is_processed = Column(Boolean, default=False)
    upload_date = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    uploader = relationship("User")