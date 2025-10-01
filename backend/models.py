# models.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Text, TIMESTAMP, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
import enum
from sqlalchemy.sql import func

class RoleEnum(str, enum.Enum):
    Student = "Student"
    Faculty = "Faculty"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    department = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete")
    faculty = relationship("Faculty", uselist=False, back_populates="user", cascade="all, delete")

class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    roll_no = Column(String(50), unique=True, nullable=False)
    class_name = Column(String(50))
    year = Column(Integer)
    section = Column(String(10))

    user = relationship("User", back_populates="student")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="student", cascade="all, delete")

class Faculty(Base):
    __tablename__ = "faculty"
    faculty_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    designation = Column(String(50))
    dept = Column(String(100))

    user = relationship("User", back_populates="faculty")
    subjects = relationship("Subject", back_populates="faculty", cascade="all, delete")
    notifications = relationship("Notification", back_populates="creator", cascade="all, delete")

class Subject(Base):
    __tablename__ = "subjects"
    subject_id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)
    semester = Column(Integer)

    faculty = relationship("Faculty", back_populates="subjects")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete")
    timetable_entries = relationship("Timetable", back_populates="subject", cascade="all, delete")

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
    status = Column(String(10))  # 'Present' or 'Absent'
    marked_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (UniqueConstraint('student_id', 'subject_id', 'date', name='u_student_subject_date'),)

    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("faculty.faculty_id", ondelete="CASCADE"))
    visible_to = Column(String(10), default="All")  # Student|Faculty|All
    created_at = Column(TIMESTAMP, server_default=func.now())

    creator = relationship("Faculty", back_populates="notifications")
