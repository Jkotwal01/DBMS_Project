#!/usr/bin/env python3
"""
Seed data script for ERP system
Creates initial users, permissions, and sample data
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
import crud
from datetime import date, datetime

def create_default_permissions(db: Session):
    """Create default permissions for the system"""
    permissions = [
        # Student permissions
        {"name": "view_own_profile", "resource": "profile", "action": "read", "description": "View own profile"},
        {"name": "edit_own_profile", "resource": "profile", "action": "update", "description": "Edit own profile"},
        {"name": "view_own_attendance", "resource": "attendance", "action": "read", "description": "View own attendance"},
        {"name": "view_own_grades", "resource": "grades", "action": "read", "description": "View own grades"},
        {"name": "view_timetable", "resource": "timetable", "action": "read", "description": "View timetable"},
        {"name": "view_notifications", "resource": "notifications", "action": "read", "description": "View notifications"},
        
        # Faculty permissions
        {"name": "manage_students", "resource": "students", "action": "create", "description": "Create student records"},
        {"name": "view_students", "resource": "students", "action": "read", "description": "View student records"},
        {"name": "update_students", "resource": "students", "action": "update", "description": "Update student records"},
        {"name": "mark_attendance", "resource": "attendance", "action": "create", "description": "Mark student attendance"},
        {"name": "view_attendance", "resource": "attendance", "action": "read", "description": "View attendance records"},
        {"name": "manage_grades", "resource": "grades", "action": "create", "description": "Create grade records"},
        {"name": "update_grades", "resource": "grades", "action": "update", "description": "Update grade records"},
        {"name": "view_grades", "resource": "grades", "action": "read", "description": "View grade records"},
        {"name": "create_notifications", "resource": "notifications", "action": "create", "description": "Create notifications"},
        {"name": "manage_timetable", "resource": "timetable", "action": "create", "description": "Manage timetable"},
        {"name": "manage_subjects", "resource": "subjects", "action": "create", "description": "Manage subjects"},
        
        # Admin permissions
        {"name": "manage_users", "resource": "users", "action": "create", "description": "Manage all users"},
        {"name": "view_users", "resource": "users", "action": "read", "description": "View all users"},
        {"name": "update_users", "resource": "users", "action": "update", "description": "Update all users"},
        {"name": "delete_users", "resource": "users", "action": "delete", "description": "Delete users"},
        {"name": "manage_permissions", "resource": "permissions", "action": "create", "description": "Manage permissions"},
        {"name": "view_audit_logs", "resource": "audit_logs", "action": "read", "description": "View audit logs"},
        {"name": "manage_system_settings", "resource": "system_settings", "action": "create", "description": "Manage system settings"},
        {"name": "bulk_upload", "resource": "students", "action": "bulk_create", "description": "Bulk upload students"},
    ]
    
    created_permissions = []
    for perm_data in permissions:
        existing = db.query(models.Permission).filter(models.Permission.name == perm_data["name"]).first()
        if not existing:
            permission = crud.create_permission(db, schemas.PermissionCreate(**perm_data))
            created_permissions.append(permission)
            print(f"Created permission: {permission.name}")
    
    return created_permissions

def create_sample_users(db: Session):
    """Create sample users for testing"""
    users_data = [
        {
            "name": "System Administrator",
            "email": "admin@erp.edu",
            "password": "admin123",
            "role": "Admin",
            "department": "IT",
            "phone": "+1234567890",
            "address": "Admin Office"
        },
        {
            "name": "Dr. John Smith",
            "email": "john.smith@erp.edu",
            "password": "faculty123",
            "role": "Faculty",
            "department": "Computer Science",
            "phone": "+1234567891",
            "address": "Faculty Block A"
        },
        {
            "name": "Prof. Sarah Johnson",
            "email": "sarah.johnson@erp.edu",
            "password": "faculty123",
            "role": "Faculty",
            "department": "Mathematics",
            "phone": "+1234567892",
            "address": "Faculty Block B"
        },
        {
            "name": "Alice Brown",
            "email": "alice.brown@student.erp.edu",
            "password": "student123",
            "role": "Student",
            "department": "Computer Science",
            "phone": "+1234567893",
            "address": "Hostel Block A"
        },
        {
            "name": "Bob Wilson",
            "email": "bob.wilson@student.erp.edu",
            "password": "student123",
            "role": "Student",
            "department": "Computer Science",
            "phone": "+1234567894",
            "address": "Hostel Block B"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        try:
            existing = db.query(models.User).filter(models.User.email == user_data["email"]).first()
            if not existing:
                user = crud.create_user(db, schemas.UserCreate(**user_data))
                created_users.append(user)
                print(f"Created user: {user.name} ({user.role})")
            else:
                created_users.append(existing)
                print(f"User already exists: {existing.name}")
        except Exception as e:
            print(f"Error creating user {user_data['name']}: {str(e)}")
    
    return created_users

def create_role_profiles(db: Session, users: list):
    """Create role-specific profiles for users"""
    for user in users:
        try:
            if user.role.value == "Faculty":
                existing_faculty = db.query(models.Faculty).filter(models.Faculty.faculty_id == user.user_id).first()
                if not existing_faculty:
                    faculty_data = {
                        "designation": "Assistant Professor" if "Dr." in user.name else "Professor",
                        "dept": user.department,
                        "employee_id": f"FAC{user.user_id:04d}",
                        "joining_date": date(2020, 1, 1),
                        "qualification": "PhD" if "Dr." in user.name else "M.Tech",
                        "experience_years": 5,
                        "salary": 80000
                    }
                    faculty = crud.create_faculty_profile(db, user.user_id, schemas.FacultyCreate(**faculty_data))
                    print(f"Created faculty profile for: {user.name}")
            
            elif user.role.value == "Student":
                existing_student = db.query(models.Student).filter(models.Student.student_id == user.user_id).first()
                if not existing_student:
                    student_data = {
                        "roll_no": f"CS{user.user_id:04d}",
                        "class_name": "B.Tech Computer Science",
                        "year": 2,
                        "section": "A",
                        "admission_date": date(2023, 8, 1),
                        "guardian_name": f"Parent of {user.name.split()[0]}",
                        "guardian_phone": "+1234567800",
                        "blood_group": "O+",
                        "date_of_birth": date(2002, 1, 1),
                        "gender": "Male" if user.name.split()[0] in ["Bob", "John"] else "Female"
                    }
                    student = crud.create_student_profile(db, user.user_id, schemas.StudentCreate(**student_data))
                    print(f"Created student profile for: {user.name}")
            
            elif user.role.value == "Admin":
                existing_admin = db.query(models.Admin).filter(models.Admin.admin_id == user.user_id).first()
                if not existing_admin:
                    admin_data = {
                        "employee_id": f"ADM{user.user_id:04d}",
                        "access_level": 3  # Super Admin
                    }
                    admin = models.Admin(
                        admin_id=user.user_id,
                        employee_id=admin_data["employee_id"],
                        access_level=admin_data["access_level"]
                    )
                    db.add(admin)
                    db.commit()
                    db.refresh(admin)
                    print(f"Created admin profile for: {user.name}")
        
        except Exception as e:
            print(f"Error creating profile for {user.name}: {str(e)}")

def create_sample_subjects(db: Session, faculty_users: list):
    """Create sample subjects"""
    subjects_data = [
        {
            "subject_name": "Data Structures and Algorithms",
            "subject_code": "CS201",
            "semester": 3,
            "credits": 4,
            "description": "Fundamental data structures and algorithms"
        },
        {
            "subject_name": "Database Management Systems",
            "subject_code": "CS301",
            "semester": 5,
            "credits": 4,
            "description": "Relational databases and SQL"
        },
        {
            "subject_name": "Calculus and Linear Algebra",
            "subject_code": "MA101",
            "semester": 1,
            "credits": 4,
            "description": "Mathematical foundations"
        },
        {
            "subject_name": "Web Development",
            "subject_code": "CS401",
            "semester": 7,
            "credits": 3,
            "description": "Full-stack web development"
        }
    ]
    
    created_subjects = []
    faculty_list = [u for u in faculty_users if u.role.value == "Faculty"]
    
    for i, subject_data in enumerate(subjects_data):
        try:
            existing = db.query(models.Subject).filter(models.Subject.subject_code == subject_data["subject_code"]).first()
            if not existing:
                # Assign faculty to subjects
                if faculty_list:
                    faculty = faculty_list[i % len(faculty_list)]
                    subject_data["faculty_id"] = faculty.user_id
                
                subject = crud.create_subject(db, schemas.SubjectCreate(**subject_data))
                created_subjects.append(subject)
                print(f"Created subject: {subject.subject_name}")
        except Exception as e:
            print(f"Error creating subject {subject_data['subject_name']}: {str(e)}")
    
    return created_subjects

def create_sample_notifications(db: Session, faculty_users: list):
    """Create sample notifications"""
    faculty_list = [u for u in faculty_users if u.role.value == "Faculty"]
    if not faculty_list:
        return
    
    notifications_data = [
        {
            "title": "Welcome to ERP System",
            "description": "Welcome to our new Enhanced ERP System. Please update your profile information.",
            "visible_to": "All",
            "priority": "Medium"
        },
        {
            "title": "Mid-term Examinations",
            "description": "Mid-term examinations will be conducted from next week. Please check the timetable.",
            "visible_to": "Student",
            "priority": "High"
        },
        {
            "title": "Faculty Meeting",
            "description": "Monthly faculty meeting scheduled for tomorrow at 2 PM in Conference Room.",
            "visible_to": "Faculty",
            "priority": "Medium"
        }
    ]
    
    for notif_data in notifications_data:
        try:
            faculty = faculty_list[0]  # Use first faculty member
            faculty_profile = db.query(models.Faculty).filter(models.Faculty.faculty_id == faculty.user_id).first()
            if faculty_profile:
                notification = crud.create_notification(db, schemas.NotificationCreate(**notif_data), faculty_profile.faculty_id)
                print(f"Created notification: {notification.title}")
        except Exception as e:
            print(f"Error creating notification {notif_data['title']}: {str(e)}")

def create_system_settings(db: Session):
    """Create default system settings"""
    settings = [
        {"key": "system_name", "value": "Enhanced ERP System", "description": "Name of the ERP system"},
        {"key": "academic_year", "value": "2024-25", "description": "Current academic year"},
        {"key": "semester", "value": "1", "description": "Current semester"},
        {"key": "attendance_threshold", "value": "75", "description": "Minimum attendance percentage required"},
        {"key": "max_login_attempts", "value": "5", "description": "Maximum login attempts before account lockout"},
        {"key": "session_timeout", "value": "1440", "description": "Session timeout in minutes"},
    ]
    
    for setting_data in settings:
        try:
            crud.set_system_setting(db, **setting_data)
            print(f"Created system setting: {setting_data['key']}")
        except Exception as e:
            print(f"Error creating system setting {setting_data['key']}: {str(e)}")

def main():
    """Main function to seed the database"""
    print("Starting database seeding...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create permissions
        print("\n1. Creating default permissions...")
        permissions = create_default_permissions(db)
        
        # Create sample users
        print("\n2. Creating sample users...")
        users = create_sample_users(db)
        
        # Create role-specific profiles
        print("\n3. Creating role-specific profiles...")
        create_role_profiles(db, users)
        
        # Create sample subjects
        print("\n4. Creating sample subjects...")
        subjects = create_sample_subjects(db, users)
        
        # Create sample notifications
        print("\n5. Creating sample notifications...")
        create_sample_notifications(db, users)
        
        # Create system settings
        print("\n6. Creating system settings...")
        create_system_settings(db)
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📋 Sample Login Credentials:")
        print("Admin: admin@erp.edu / admin123")
        print("Faculty: john.smith@erp.edu / faculty123")
        print("Faculty: sarah.johnson@erp.edu / faculty123")
        print("Student: alice.brown@student.erp.edu / student123")
        print("Student: bob.wilson@student.erp.edu / student123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()