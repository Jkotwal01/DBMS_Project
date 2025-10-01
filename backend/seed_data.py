# seed_data.py - Seed data for ERP system
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models_v2 import *
from crud_v2 import *
from auth_v2 import SecurityManager
from datetime import date, datetime, timedelta
import json

def create_seed_data():
    """Create initial seed data for the ERP system"""
    db = SessionLocal()
    
    try:
        print("Creating seed data...")
        
        # Create departments
        departments_data = [
            {"dept_name": "Computer Science", "dept_code": "CS", "description": "Computer Science Department"},
            {"dept_name": "Information Technology", "dept_code": "IT", "description": "Information Technology Department"},
            {"dept_name": "Electronics", "dept_code": "ECE", "description": "Electronics and Communication Engineering"},
            {"dept_name": "Mechanical", "dept_code": "ME", "description": "Mechanical Engineering"},
            {"dept_name": "Civil", "dept_code": "CE", "description": "Civil Engineering"}
        ]
        
        departments = []
        for dept_data in departments_data:
            existing_dept = db.query(Department).filter(Department.dept_code == dept_data["dept_code"]).first()
            if not existing_dept:
                dept = Department(**dept_data)
                db.add(dept)
                departments.append(dept)
        
        db.commit()
        print(f"Created {len(departments)} departments")
        
        # Create academic year
        academic_year = AcademicYear(
            year_name="2024-2025",
            start_date=date(2024, 7, 1),
            end_date=date(2025, 6, 30),
            is_current=True
        )
        db.add(academic_year)
        db.commit()
        
        # Create semester
        semester = Semester(
            semester_name="Fall 2024",
            academic_year_id=academic_year.year_id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 12, 31),
            is_current=True
        )
        db.add(semester)
        db.commit()
        
        # Create admin user
        admin_user_data = {
            "name": "System Administrator",
            "email": "admin@erp.edu",
            "password": "admin123",
            "role": RoleEnum.ADMIN,
            "department": "IT",
            "phone": "+1234567890",
            "status": StatusEnum.ACTIVE
        }
        
        existing_admin = user_crud.get_by_email(db, admin_user_data["email"])
        if not existing_admin:
            admin_user = user_crud.create_user(db, UserCreate(**admin_user_data))
            
            # Create admin profile
            admin_profile = Admin(
                admin_id=admin_user.user_id,
                employee_id="ADMIN001",
                designation="System Administrator",
                dept_id=departments[1].dept_id,  # IT department
                permissions=json.dumps(["all"]),
                joining_date=date.today()
            )
            db.add(admin_profile)
            db.commit()
            print(f"Created admin user: {admin_user.email}")
        
        # Create faculty users
        faculty_data = [
            {
                "name": "Dr. John Smith",
                "email": "john.smith@erp.edu",
                "password": "faculty123",
                "role": RoleEnum.FACULTY,
                "department": "CS",
                "phone": "+1234567891",
                "employee_id": "FAC001",
                "designation": "Professor",
                "qualification": "PhD in Computer Science",
                "specialization": "Machine Learning",
                "experience_years": 15
            },
            {
                "name": "Dr. Sarah Johnson",
                "email": "sarah.johnson@erp.edu",
                "password": "faculty123",
                "role": RoleEnum.FACULTY,
                "department": "IT",
                "phone": "+1234567892",
                "employee_id": "FAC002",
                "designation": "Associate Professor",
                "qualification": "PhD in Information Technology",
                "specialization": "Database Systems",
                "experience_years": 10
            },
            {
                "name": "Dr. Michael Brown",
                "email": "michael.brown@erp.edu",
                "password": "faculty123",
                "role": RoleEnum.FACULTY,
                "department": "ECE",
                "phone": "+1234567893",
                "employee_id": "FAC003",
                "designation": "Assistant Professor",
                "qualification": "PhD in Electronics",
                "specialization": "Signal Processing",
                "experience_years": 8
            }
        ]
        
        faculty_users = []
        for fac_data in faculty_data:
            existing_faculty = user_crud.get_by_email(db, fac_data["email"])
            if not existing_faculty:
                # Find department
                dept = db.query(Department).filter(Department.dept_code == fac_data["department"]).first()
                
                # Create user
                user_data = {k: v for k, v in fac_data.items() if k not in ["employee_id", "designation", "qualification", "specialization", "experience_years"]}
                faculty_user = user_crud.create_user(db, UserCreate(**user_data))
                
                # Create faculty profile
                faculty_profile = Faculty(
                    faculty_id=faculty_user.user_id,
                    employee_id=fac_data["employee_id"],
                    designation=fac_data["designation"],
                    dept_id=dept.dept_id if dept else None,
                    qualification=fac_data["qualification"],
                    specialization=fac_data["specialization"],
                    experience_years=fac_data["experience_years"],
                    joining_date=date.today()
                )
                db.add(faculty_profile)
                faculty_users.append(faculty_user)
        
        db.commit()
        print(f"Created {len(faculty_users)} faculty users")
        
        # Create student users
        student_data = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@student.erp.edu",
                "password": "student123",
                "role": RoleEnum.STUDENT,
                "department": "CS",
                "phone": "+1234567894",
                "roll_no": "CS2024001",
                "class_name": "B.Tech CSE",
                "year": 2024,
                "section": "A",
                "batch": "2024"
            },
            {
                "name": "Bob Smith",
                "email": "bob.smith@student.erp.edu",
                "password": "student123",
                "role": RoleEnum.STUDENT,
                "department": "IT",
                "phone": "+1234567895",
                "roll_no": "IT2024002",
                "class_name": "B.Tech IT",
                "year": 2024,
                "section": "B",
                "batch": "2024"
            },
            {
                "name": "Charlie Brown",
                "email": "charlie.brown@student.erp.edu",
                "password": "student123",
                "role": RoleEnum.STUDENT,
                "department": "ECE",
                "phone": "+1234567896",
                "roll_no": "ECE2024003",
                "class_name": "B.Tech ECE",
                "year": 2024,
                "section": "A",
                "batch": "2024"
            },
            {
                "name": "Diana Wilson",
                "email": "diana.wilson@student.erp.edu",
                "password": "student123",
                "role": RoleEnum.STUDENT,
                "department": "CS",
                "phone": "+1234567897",
                "roll_no": "CS2024004",
                "class_name": "B.Tech CSE",
                "year": 2024,
                "section": "B",
                "batch": "2024"
            },
            {
                "name": "Eve Davis",
                "email": "eve.davis@student.erp.edu",
                "password": "student123",
                "role": RoleEnum.STUDENT,
                "department": "ME",
                "phone": "+1234567898",
                "roll_no": "ME2024005",
                "class_name": "B.Tech ME",
                "year": 2024,
                "section": "A",
                "batch": "2024"
            }
        ]
        
        student_users = []
        for std_data in student_data:
            existing_student = user_crud.get_by_email(db, std_data["email"])
            if not existing_student:
                # Find department
                dept = db.query(Department).filter(Department.dept_code == std_data["department"]).first()
                
                # Create user
                user_data = {k: v for k, v in std_data.items() if k not in ["roll_no", "class_name", "year", "section", "batch"]}
                student_user = user_crud.create_user(db, UserCreate(**user_data))
                
                # Create student profile
                student_profile = Student(
                    student_id=student_user.user_id,
                    roll_no=std_data["roll_no"],
                    class_name=std_data["class_name"],
                    year=std_data["year"],
                    section=std_data["section"],
                    batch=std_data["batch"],
                    dept_id=dept.dept_id if dept else None,
                    current_semester_id=semester.semester_id,
                    enrollment_date=date.today(),
                    emergency_contact="Parent/Guardian",
                    emergency_phone="+1234567899"
                )
                db.add(student_profile)
                student_users.append(student_user)
        
        db.commit()
        print(f"Created {len(student_users)} student users")
        
        # Create subjects
        subjects_data = [
            {
                "subject_code": "CS101",
                "subject_name": "Programming Fundamentals",
                "credits": 4,
                "semester": 1,
                "description": "Introduction to programming concepts",
                "department": "CS"
            },
            {
                "subject_code": "CS102",
                "subject_name": "Data Structures",
                "credits": 4,
                "semester": 2,
                "description": "Data structures and algorithms",
                "department": "CS"
            },
            {
                "subject_code": "IT101",
                "subject_name": "Database Management",
                "credits": 3,
                "semester": 1,
                "description": "Database design and management",
                "department": "IT"
            },
            {
                "subject_code": "ECE101",
                "subject_name": "Digital Electronics",
                "credits": 4,
                "semester": 1,
                "description": "Digital circuit design",
                "department": "ECE"
            },
            {
                "subject_code": "ME101",
                "subject_name": "Engineering Mechanics",
                "credits": 4,
                "semester": 1,
                "description": "Basic mechanics principles",
                "department": "ME"
            }
        ]
        
        subjects = []
        for subj_data in subjects_data:
            existing_subject = db.query(Subject).filter(Subject.subject_code == subj_data["subject_code"]).first()
            if not existing_subject:
                # Find department
                dept = db.query(Department).filter(Department.dept_code == subj_data["department"]).first()
                
                # Find faculty for this department
                faculty = db.query(Faculty).filter(Faculty.dept_id == dept.dept_id).first()
                
                subject = Subject(
                    subject_code=subj_data["subject_code"],
                    subject_name=subj_data["subject_name"],
                    faculty_id=faculty.faculty_id if faculty else None,
                    dept_id=dept.dept_id if dept else None,
                    credits=subj_data["credits"],
                    semester=subj_data["semester"],
                    description=subj_data["description"]
                )
                db.add(subject)
                subjects.append(subject)
        
        db.commit()
        print(f"Created {len(subjects)} subjects")
        
        # Create timetable entries
        timetable_data = [
            {
                "subject_code": "CS101",
                "day": "Monday",
                "start_time": "09:00",
                "end_time": "10:30",
                "class_room": "CS-101"
            },
            {
                "subject_code": "CS101",
                "day": "Wednesday",
                "start_time": "09:00",
                "end_time": "10:30",
                "class_room": "CS-101"
            },
            {
                "subject_code": "IT101",
                "day": "Tuesday",
                "start_time": "11:00",
                "end_time": "12:30",
                "class_room": "IT-201"
            },
            {
                "subject_code": "IT101",
                "day": "Thursday",
                "start_time": "11:00",
                "end_time": "12:30",
                "class_room": "IT-201"
            },
            {
                "subject_code": "ECE101",
                "day": "Monday",
                "start_time": "14:00",
                "end_time": "15:30",
                "class_room": "ECE-301"
            },
            {
                "subject_code": "ECE101",
                "day": "Wednesday",
                "start_time": "14:00",
                "end_time": "15:30",
                "class_room": "ECE-301"
            }
        ]
        
        timetable_entries = []
        for tt_data in timetable_data:
            subject = db.query(Subject).filter(Subject.subject_code == tt_data["subject_code"]).first()
            if subject:
                timetable_entry = Timetable(
                    subject_id=subject.subject_id,
                    faculty_id=subject.faculty_id,
                    class_room=tt_data["class_room"],
                    day=tt_data["day"],
                    start_time=tt_data["start_time"],
                    end_time=tt_data["end_time"],
                    semester_id=semester.semester_id,
                    is_active=True
                )
                db.add(timetable_entry)
                timetable_entries.append(timetable_entry)
        
        db.commit()
        print(f"Created {len(timetable_entries)} timetable entries")
        
        # Create sample notifications
        notifications_data = [
            {
                "title": "Welcome to ERP System",
                "message": "Welcome to the new ERP Attendance Management System. Please explore the features and update your profiles.",
                "notification_type": NotificationTypeEnum.GENERAL,
                "target_role": RoleEnum.STUDENT,
                "is_broadcast": True,
                "created_by": faculty_users[0].user_id if faculty_users else None
            },
            {
                "title": "Faculty Meeting",
                "message": "Monthly faculty meeting scheduled for next Friday at 2:00 PM in the conference room.",
                "notification_type": NotificationTypeEnum.ADMINISTRATIVE,
                "target_role": RoleEnum.FACULTY,
                "is_broadcast": True,
                "created_by": faculty_users[0].user_id if faculty_users else None
            },
            {
                "title": "System Maintenance",
                "message": "System maintenance scheduled for this Sunday from 2:00 AM to 6:00 AM. The system will be temporarily unavailable.",
                "notification_type": NotificationTypeEnum.GENERAL,
                "target_role": None,  # All users
                "is_broadcast": True,
                "created_by": admin_user.user_id if 'admin_user' in locals() else None
            }
        ]
        
        notifications = []
        for notif_data in notifications_data:
            notification = Notification(**notif_data)
            db.add(notification)
            notifications.append(notification)
        
        db.commit()
        print(f"Created {len(notifications)} notifications")
        
        print("\n=== SEED DATA SUMMARY ===")
        print(f"Departments: {len(departments)}")
        print(f"Academic Year: {academic_year.year_name}")
        print(f"Semester: {semester.semester_name}")
        print(f"Faculty Users: {len(faculty_users)}")
        print(f"Student Users: {len(student_users)}")
        print(f"Subjects: {len(subjects)}")
        print(f"Timetable Entries: {len(timetable_entries)}")
        print(f"Notifications: {len(notifications)}")
        
        print("\n=== TEST CREDENTIALS ===")
        print("Admin:")
        print("  Email: admin@erp.edu")
        print("  Password: admin123")
        print("\nFaculty:")
        print("  Email: john.smith@erp.edu")
        print("  Password: faculty123")
        print("\nStudents:")
        print("  Email: alice.johnson@student.erp.edu")
        print("  Password: student123")
        print("  Email: bob.smith@student.erp.edu")
        print("  Password: student123")
        
        print("\nSeed data created successfully!")
        
    except Exception as e:
        print(f"Error creating seed data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()