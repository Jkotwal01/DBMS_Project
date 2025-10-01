#!/usr/bin/env python3
"""
Simple script to create users with working password hashing
"""

from sqlalchemy.orm import Session
from database import SessionLocal
import models
import hashlib

def simple_hash(password: str) -> str:
    """Simple SHA256 hash for testing purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    db = SessionLocal()
    try:
        # Create admin user
        admin = models.User(
            name="System Administrator",
            email="admin@erp.edu",
            password_hash=simple_hash("admin123"),
            role="Admin",
            department="IT",
            phone="+1234567890",
            address="Admin Office"
        )
        
        # Create faculty user
        faculty = models.User(
            name="Dr. John Smith",
            email="john.smith@erp.edu",
            password_hash=simple_hash("faculty123"),
            role="Faculty",
            department="Computer Science",
            phone="+1234567891",
            address="Faculty Block A"
        )
        
        # Create student user
        student = models.User(
            name="Alice Brown",
            email="alice.brown@student.erp.edu",
            password_hash=simple_hash("student123"),
            role="Student",
            department="Computer Science",
            phone="+1234567893",
            address="Hostel Block A"
        )
        
        # Check if users already exist
        existing_admin = db.query(models.User).filter(models.User.email == "admin@erp.edu").first()
        existing_faculty = db.query(models.User).filter(models.User.email == "john.smith@erp.edu").first()
        existing_student = db.query(models.User).filter(models.User.email == "alice.brown@student.erp.edu").first()
        
        if not existing_admin:
            db.add(admin)
            print("Created admin user")
        
        if not existing_faculty:
            db.add(faculty)
            print("Created faculty user")
            
        if not existing_student:
            db.add(student)
            print("Created student user")
        
        db.commit()
        
        # Get user IDs for profile creation
        admin_user = db.query(models.User).filter(models.User.email == "admin@erp.edu").first()
        faculty_user = db.query(models.User).filter(models.User.email == "john.smith@erp.edu").first()
        student_user = db.query(models.User).filter(models.User.email == "alice.brown@student.erp.edu").first()
        
        # Create profiles
        if admin_user:
            existing_admin_profile = db.query(models.Admin).filter(models.Admin.admin_id == admin_user.user_id).first()
            if not existing_admin_profile:
                admin_profile = models.Admin(
                    admin_id=admin_user.user_id,
                    employee_id=f"ADM{admin_user.user_id:04d}",
                    access_level=3
                )
                db.add(admin_profile)
                print("Created admin profile")
        
        if faculty_user:
            existing_faculty_profile = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty_user.user_id).first()
            if not existing_faculty_profile:
                faculty_profile = models.Faculty(
                    faculty_id=faculty_user.user_id,
                    designation="Assistant Professor",
                    dept=faculty_user.department,
                    employee_id=f"FAC{faculty_user.user_id:04d}",
                    joining_date="2020-01-01",
                    qualification="PhD",
                    experience_years=5,
                    salary=80000
                )
                db.add(faculty_profile)
                print("Created faculty profile")
        
        if student_user:
            existing_student_profile = db.query(models.Student).filter(models.Student.student_id == student_user.user_id).first()
            if not existing_student_profile:
                student_profile = models.Student(
                    student_id=student_user.user_id,
                    roll_no=f"CS{student_user.user_id:04d}",
                    class_name="B.Tech Computer Science",
                    year=2,
                    section="A",
                    admission_date="2023-08-01",
                    guardian_name="Parent of Alice",
                    guardian_phone="+1234567800",
                    blood_group="O+",
                    date_of_birth="2002-01-01",
                    gender="Female"
                )
                db.add(student_profile)
                print("Created student profile")
        
        db.commit()
        print("✅ Users created successfully!")
        print("\n📋 Login Credentials:")
        print("Admin: admin@erp.edu / admin123")
        print("Faculty: john.smith@erp.edu / faculty123")
        print("Student: alice.brown@student.erp.edu / student123")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()