# models.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Text, TIMESTAMP, Enum as SAEnum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum
from sqlalchemy.sql import func

class RoleEnum(str, enum.Enum):
    """User roles - Extensible for future roles like Admin, Parent, Management"""
    Student = "Student"
    Faculty = "Faculty"
    Admin = "Admin"  # For future use
    Parent = "Parent"  # For future use
    Management = "Management"  # For future use

class User(Base):
    """
    Base user table for authentication and common user data.
    All users (Student, Faculty, Admin, etc.) have an entry here.
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False, index=True)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)  # For soft delete/deactivation
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete")
    faculty = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete")

class Student(Base):
    """
    Student-specific profile information.
    One-to-one relationship with User table.
    """
    __tablename__ = "students"
    
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    roll_no = Column(String(50), unique=True, nullable=False, index=True)
    class_name = Column(String(50))
    year = Column(Integer)
    section = Column(String(10))
    division = Column(String(10))
    batch = Column(String(50))
    admission_date = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="student", cascade="all, delete")

class Faculty(Base):
    """
    Faculty-specific profile information.
    One-to-one relationship with User table.
    """
    __tablename__ = "faculty"
    
    faculty_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=True)
    designation = Column(String(50))
    dept = Column(String(100))
    specialization = Column(String(100), nullable=True)
    joining_date = Column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="faculty")
    subjects = relationship("Subject", back_populates="faculty", cascade="all, delete")
    notifications = relationship("Notification", back_populates="creator", cascade="all, delete")
    attendance_marked = relationship("Attendance", back_populates="marked_by_faculty", cascade="all, delete")

class Subject(Base):
    """
    Subject/Course information.
    Can be assigned to faculty members.
    """
    __tablename__ = "subjects"
    
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String(20), unique=True, nullable=True)
    subject_name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    semester = Column(Integer)
    credits = Column(Integer, default=3)
    department = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    faculty = relationship("Faculty", back_populates="subjects")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="subject", cascade="all, delete")

class Timetable(Base):
    """
    Timetable entries for students.
    Maps subjects to students with day and time information.
    """
    __tablename__ = "timetable"
    
    timetable_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    day = Column(String(10))  # 'Monday', 'Tuesday', etc.
    time_slot = Column(String(30))  # e.g., '09:00-10:00'
    room_number = Column(String(20), nullable=True)
    semester = Column(Integer, nullable=True)
    academic_year = Column(String(20), nullable=True)  # e.g., '2024-2025'
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (UniqueConstraint('student_id', 'day', 'time_slot', name='u_student_day_time'),)

    # Relationships
    subject = relationship("Subject", back_populates="timetable_entries")
    student = relationship("Student", back_populates="timetable_entries")

class Attendance(Base):
    """
    Attendance records for students.
    Tracks who marked the attendance for audit purposes.
    """
    __tablename__ = "attendance"
    
    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"))
    date = Column(Date, index=True)
    status = Column(String(10))  # 'Present', 'Absent', 'Late', 'Excused'
    marked_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('student_id', 'subject_id', 'date', name='u_student_subject_date'),)

    # Relationships
    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")
    marked_by_faculty = relationship("Faculty", back_populates="attendance_marked")

class Notification(Base):
    """
    Notification system for broadcasting messages.
    Supports role-based visibility.
    """
    __tablename__ = "notifications"
    
    notification_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="CASCADE"))
    visible_to = Column(String(20), default="Student")  # 'Student', 'Faculty', 'All', 'Admin', etc.
    priority = Column(String(10), default="normal")  # 'low', 'normal', 'high', 'urgent'
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("Faculty", back_populates="notifications")
