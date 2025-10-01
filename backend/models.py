# models.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Text, TIMESTAMP, Enum as SAEnum, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
import enum
from sqlalchemy.sql import func

class RoleEnum(str, enum.Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    EXCUSED = "Excused"

class NotificationPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete")
    faculty = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete")
    admin = relationship("Admin", uselist=False, back_populates="user", cascade="all, delete")
    parent = relationship("Parent", uselist=False, back_populates="user", cascade="all, delete")
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete", foreign_keys="UserPermission.user_id")

class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    roll_no = Column(String(50), unique=True, nullable=False)
    class_name = Column(String(50))
    year = Column(Integer)
    section = Column(String(10))
    admission_date = Column(Date, nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.parent_id", ondelete="SET NULL"), nullable=True)
    guardian_name = Column(String(100), nullable=True)
    guardian_phone = Column(String(20), nullable=True)
    blood_group = Column(String(5), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)

    user = relationship("User", back_populates="student")
    parent = relationship("Parent", back_populates="children")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="student", cascade="all, delete")
    grades = relationship("Grade", back_populates="student", cascade="all, delete")

class Faculty(Base):
    __tablename__ = "faculty"
    faculty_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    designation = Column(String(50))
    dept = Column(String(100))
    employee_id = Column(String(50), unique=True, nullable=True)
    joining_date = Column(Date, nullable=True)
    qualification = Column(String(200), nullable=True)
    experience_years = Column(Integer, nullable=True)
    salary = Column(Integer, nullable=True)

    user = relationship("User", back_populates="faculty")
    subjects = relationship("Subject", back_populates="faculty", cascade="all, delete")
    notifications = relationship("Notification", back_populates="creator", cascade="all, delete")
    attendance_marked = relationship("Attendance", back_populates="marked_by_faculty", cascade="all, delete")

class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    subject_code = Column(String(20), unique=True, nullable=True)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    semester = Column(Integer)
    credits = Column(Integer, default=3)
    description = Column(Text, nullable=True)

    faculty = relationship("Faculty", back_populates="subjects")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="subject", cascade="all, delete")
    grades = relationship("Grade", back_populates="subject", cascade="all, delete")

class Timetable(Base):
    __tablename__ = "timetable"
    class_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    day = Column(String(10))  # 'Mon','Tue', etc.
    time_slot = Column(String(30))

    subject = relationship("Subject", back_populates="timetable_entries")
    student = relationship("Student", back_populates="timetable_entries")

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"))
    date = Column(Date)
    status = Column(SAEnum(AttendanceStatus), nullable=False)
    marked_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    marked_at = Column(TIMESTAMP, server_default=func.now())
    remarks = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint('student_id', 'subject_id', 'date', name='u_student_subject_date'),)

    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")
    marked_by_faculty = relationship("Faculty", back_populates="attendance_marked")

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="CASCADE"))
    visible_to = Column(String(20), default="All")  # Student|Faculty|All|Admin|Parent
    priority = Column(SAEnum(NotificationPriority), default=NotificationPriority.MEDIUM)
    is_read = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    creator = relationship("Faculty", back_populates="notifications")

# New Models for Enhanced ERP System

class Admin(Base):
    __tablename__ = "admins"
    admin_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=True)
    access_level = Column(Integer, default=1)  # 1=Basic, 2=Advanced, 3=Super Admin
    
    user = relationship("User", back_populates="admin")

class Parent(Base):
    __tablename__ = "parents"
    parent_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    occupation = Column(String(100), nullable=True)
    annual_income = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="parent")
    children = relationship("Student", back_populates="parent")

class Permission(Base):
    __tablename__ = "permissions"
    permission_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False)  # e.g., 'students', 'attendance', 'grades'
    action = Column(String(20), nullable=False)    # e.g., 'create', 'read', 'update', 'delete'
    
    user_permissions = relationship("UserPermission", back_populates="permission")

class UserPermission(Base):
    __tablename__ = "user_permissions"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id", ondelete="CASCADE"), primary_key=True)
    granted_at = Column(TIMESTAMP, server_default=func.now())
    granted_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    
    user = relationship("User", back_populates="user_permissions", foreign_keys=[user_id])
    permission = relationship("Permission", back_populates="user_permissions")

class Grade(Base):
    __tablename__ = "grades"
    grade_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"))
    exam_type = Column(String(50))  # 'Mid-term', 'Final', 'Assignment', 'Quiz'
    marks_obtained = Column(Integer)
    total_marks = Column(Integer)
    grade_letter = Column(String(5), nullable=True)  # A+, A, B+, etc.
    exam_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class SystemSettings(Base):
    __tablename__ = "system_settings"
    setting_id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
