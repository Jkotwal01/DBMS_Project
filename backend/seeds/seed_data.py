"""
Seed data for initial setup
Creates sample students, faculty, subjects, and demo accounts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from auth import hash_password
import models
from datetime import date, datetime

def create_seed_data():
    """Create initial seed data for the ERP system"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🌱 Starting seed data creation...")
        
        # Check if data already exists
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print(f"⚠️  Database already contains {existing_users} users. Skipping seed...")
            return
        
        # ========== Create Faculty Users ==========
        print("\n👨‍🏫 Creating faculty users...")
        
        faculty_data = [
            {
                'name': 'Dr. John Smith',
                'email': 'john.smith@university.edu',
                'password': 'faculty123',
                'department': 'Computer Science',
                'phone': '555-0101',
                'employee_id': 'FAC001',
                'designation': 'Professor',
                'dept': 'Computer Science',
                'specialization': 'Artificial Intelligence'
            },
            {
                'name': 'Dr. Sarah Johnson',
                'email': 'sarah.johnson@university.edu',
                'password': 'faculty123',
                'department': 'Mathematics',
                'phone': '555-0102',
                'employee_id': 'FAC002',
                'designation': 'Associate Professor',
                'dept': 'Mathematics',
                'specialization': 'Applied Mathematics'
            },
            {
                'name': 'Prof. Michael Brown',
                'email': 'michael.brown@university.edu',
                'password': 'faculty123',
                'department': 'Physics',
                'phone': '555-0103',
                'employee_id': 'FAC003',
                'designation': 'Assistant Professor',
                'dept': 'Physics',
                'specialization': 'Quantum Mechanics'
            }
        ]
        
        faculty_users = []
        for fac_data in faculty_data:
            # Create user
            user = models.User(
                name=fac_data['name'],
                email=fac_data['email'],
                password_hash=hash_password(fac_data['password']),
                role=models.RoleEnum.Faculty,
                department=fac_data['department'],
                phone=fac_data['phone'],
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Create faculty profile
            faculty = models.Faculty(
                faculty_id=user.user_id,
                employee_id=fac_data['employee_id'],
                designation=fac_data['designation'],
                dept=fac_data['dept'],
                specialization=fac_data['specialization'],
                joining_date=date(2020, 1, 1)
            )
            db.add(faculty)
            faculty_users.append(user)
            print(f"  ✅ Created: {user.name} ({user.email})")
        
        db.commit()
        
        # ========== Create Student Users ==========
        print("\n👨‍🎓 Creating student users...")
        
        student_data = [
            {
                'name': 'Alice Williams',
                'email': 'alice.williams@student.edu',
                'password': 'student123',
                'department': 'Computer Science',
                'phone': '555-1001',
                'roll_no': 'CS2024001',
                'class_name': 'Computer Science',
                'year': 2,
                'section': 'A',
                'division': '1',
                'batch': '2024'
            },
            {
                'name': 'Bob Davis',
                'email': 'bob.davis@student.edu',
                'password': 'student123',
                'department': 'Computer Science',
                'phone': '555-1002',
                'roll_no': 'CS2024002',
                'class_name': 'Computer Science',
                'year': 2,
                'section': 'A',
                'division': '1',
                'batch': '2024'
            },
            {
                'name': 'Carol Martinez',
                'email': 'carol.martinez@student.edu',
                'password': 'student123',
                'department': 'Computer Science',
                'phone': '555-1003',
                'roll_no': 'CS2024003',
                'class_name': 'Computer Science',
                'year': 2,
                'section': 'B',
                'division': '1',
                'batch': '2024'
            },
            {
                'name': 'David Garcia',
                'email': 'david.garcia@student.edu',
                'password': 'student123',
                'department': 'Mathematics',
                'phone': '555-1004',
                'roll_no': 'MATH2024001',
                'class_name': 'Mathematics',
                'year': 1,
                'section': 'A',
                'division': '1',
                'batch': '2024'
            },
            {
                'name': 'Emma Wilson',
                'email': 'emma.wilson@student.edu',
                'password': 'student123',
                'department': 'Physics',
                'phone': '555-1005',
                'roll_no': 'PHY2024001',
                'class_name': 'Physics',
                'year': 3,
                'section': 'A',
                'division': '1',
                'batch': '2024'
            }
        ]
        
        student_users = []
        for stu_data in student_data:
            # Create user
            user = models.User(
                name=stu_data['name'],
                email=stu_data['email'],
                password_hash=hash_password(stu_data['password']),
                role=models.RoleEnum.Student,
                department=stu_data['department'],
                phone=stu_data['phone'],
                is_active=True
            )
            db.add(user)
            db.flush()
            
            # Create student profile
            student = models.Student(
                student_id=user.user_id,
                roll_no=stu_data['roll_no'],
                class_name=stu_data['class_name'],
                year=stu_data['year'],
                section=stu_data['section'],
                division=stu_data['division'],
                batch=stu_data['batch'],
                admission_date=date(2024, 1, 1)
            )
            db.add(student)
            student_users.append(user)
            print(f"  ✅ Created: {user.name} ({user.email}) - Roll No: {stu_data['roll_no']}")
        
        db.commit()
        
        # ========== Create Subjects ==========
        print("\n📚 Creating subjects...")
        
        subjects_data = [
            {
                'subject_code': 'CS101',
                'subject_name': 'Data Structures and Algorithms',
                'faculty_id': faculty_users[0].user_id,
                'semester': 3,
                'credits': 4,
                'department': 'Computer Science'
            },
            {
                'subject_code': 'CS102',
                'subject_name': 'Database Management Systems',
                'faculty_id': faculty_users[0].user_id,
                'semester': 4,
                'credits': 4,
                'department': 'Computer Science'
            },
            {
                'subject_code': 'MATH201',
                'subject_name': 'Linear Algebra',
                'faculty_id': faculty_users[1].user_id,
                'semester': 2,
                'credits': 3,
                'department': 'Mathematics'
            },
            {
                'subject_code': 'PHY301',
                'subject_name': 'Quantum Physics',
                'faculty_id': faculty_users[2].user_id,
                'semester': 5,
                'credits': 4,
                'department': 'Physics'
            }
        ]
        
        created_subjects = []
        for subj_data in subjects_data:
            subject = models.Subject(**subj_data)
            db.add(subject)
            db.flush()
            created_subjects.append(subject)
            print(f"  ✅ Created: {subject.subject_code} - {subject.subject_name}")
        
        db.commit()
        
        # ========== Create Sample Notifications ==========
        print("\n📢 Creating sample notifications...")
        
        notifications_data = [
            {
                'title': 'Welcome to the New Academic Year!',
                'description': 'We are excited to welcome all students to the new academic year 2024-2025. Please check your timetable and attendance regularly.',
                'created_by': faculty_users[0].user_id,
                'visible_to': 'Student',
                'priority': 'high'
            },
            {
                'title': 'Midterm Examinations Schedule',
                'description': 'Midterm examinations will be conducted from March 15 to March 25. Please prepare accordingly.',
                'created_by': faculty_users[1].user_id,
                'visible_to': 'All',
                'priority': 'urgent'
            },
            {
                'title': 'Faculty Meeting on Monday',
                'description': 'All faculty members are requested to attend the department meeting on Monday at 10 AM.',
                'created_by': faculty_users[0].user_id,
                'visible_to': 'Faculty',
                'priority': 'normal'
            }
        ]
        
        for notif_data in notifications_data:
            notification = models.Notification(**notif_data)
            db.add(notification)
            print(f"  ✅ Created: {notification.title}")
        
        db.commit()
        
        print("\n✨ Seed data creation completed successfully!")
        print("\n📋 Summary:")
        print(f"  - Faculty users: {len(faculty_users)}")
        print(f"  - Student users: {len(student_users)}")
        print(f"  - Subjects: {len(created_subjects)}")
        print(f"  - Notifications: {len(notifications_data)}")
        
        print("\n🔑 Login Credentials:")
        print("\n  Faculty:")
        for fac_data in faculty_data:
            print(f"    📧 {fac_data['email']} | 🔒 {fac_data['password']}")
        
        print("\n  Students:")
        for stu_data in student_data[:3]:  # Show first 3
            print(f"    📧 {stu_data['email']} | 🔒 {stu_data['password']}")
        print("    ... and more")
        
    except Exception as e:
        print(f"\n❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
