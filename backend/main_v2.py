# main_v2.py - Enhanced FastAPI Application with ERP Architecture
import os
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn

# Import our modules
from database import engine, SessionLocal, Base
from models_v2 import *
from schemas_v2 import *
from crud_v2 import *
from auth_v2 import SecurityManager, AuditLogger
from deps_v2 import *

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up ERP system...")
    Base.metadata.create_all(bind=engine)
    
    # Initialize default data if needed
    await initialize_default_data()
    
    yield
    
    # Shutdown
    print("Shutting down ERP system...")

# Initialize FastAPI app
app = FastAPI(
    title="ERP Attendance Management System",
    description="A comprehensive ERP system for educational institutions with role-based access control",
    version="2.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# CORS middleware
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # Alternative React port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Enhanced login with audit logging"""
    try:
        # Authenticate user
        user = user_crud.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            # Log failed login attempt
            AuditLogger.log_login(
                db=db,
                user_id=0,  # Unknown user
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                success=False,
                failure_reason="Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if user.status != StatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)))
        access_token = SecurityManager.create_access_token(
            data={"user_id": user.user_id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        # Update last login
        user_crud.update_last_login(db, user.user_id)
        
        # Log successful login
        AuditLogger.log_login(
            db=db,
            user_id=user.user_id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            success=True
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=access_token_expires.total_seconds(),
            user_role=user.role.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login service error"
        )

@app.post("/auth/register", response_model=UserOut)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """User registration with role-based profile creation"""
    try:
        # Create user
        user = user_crud.create_user(db, user_data)
        
        # Log user creation
        AuditLogger.log_activity(
            db=db,
            user_id=user.user_id,
            action="create_user",
            table_name="users",
            record_id=user.user_id,
            new_values=user_data.dict(),
            ip_address=request.client.host if request else None
        )
        
        return user
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service error"
        )

@app.get("/auth/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@app.post("/auth/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Logout user (client should remove token)"""
    # Log logout activity
    AuditLogger.log_activity(
        db=db,
        user_id=current_user["user_id"],
        action="logout",
        table_name="users",
        record_id=current_user["user_id"],
        ip_address=request.client.host if request else None
    )
    
    return {"message": "Successfully logged out"}

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.get("/users", response_model=List[UserOut])
async def get_users(
    pagination: Dict = Depends(get_pagination_params),
    search_params: Dict = Depends(get_search_params),
    current_user: Dict[str, Any] = Depends(require_permission("read_all_profiles")),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    users = user_crud.get_multi(
        db, 
        skip=pagination["skip"], 
        limit=pagination["limit"]
    )
    return users

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    target_user: User = Depends(check_user_access),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get specific user by ID"""
    return target_user

@app.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    target_user: User = Depends(check_user_access),
    current_user: Dict[str, Any] = Depends(require_permission("update_all_profiles")),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Update user profile"""
    old_values = {
        "name": target_user.name,
        "email": target_user.email,
        "status": target_user.status.value
    }
    
    # Update user
    updated_user = user_crud.update(db, target_user, user_update)
    
    # Log activity
    AuditLogger.log_activity(
        db=db,
        user_id=current_user["user_id"],
        action="update_user",
        table_name="users",
        record_id=user_id,
        old_values=old_values,
        new_values=user_update.dict(exclude_unset=True),
        ip_address=request.client.host if request else None
    )
    
    return updated_user

# ==================== STUDENT ENDPOINTS ====================

@app.get("/students", response_model=List[StudentWithUser])
async def get_students(
    pagination: Dict = Depends(get_pagination_params),
    dept_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(require_permission("read_student_profiles")),
    db: Session = Depends(get_db)
):
    """Get all students"""
    if dept_id:
        students = student_crud.get_students_by_department(db, dept_id, **pagination)
    else:
        students = student_crud.get_multi(db, **pagination)
    return students

@app.get("/students/{student_id}", response_model=StudentWithUser)
async def get_student(
    student_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific student"""
    # Check access permissions
    if current_user["user_id"] != student_id and current_user["role"] not in ["Faculty", "Admin", "Management"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    student = student_crud.get_with_user(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/students/{student_id}/profile", response_model=StudentOut)
async def create_student_profile(
    student_id: int,
    profile_data: StudentCreate,
    current_user: Dict[str, Any] = Depends(require_role(["Student", "Admin"])),
    db: Session = Depends(get_db)
):
    """Create student profile"""
    # Check if user can create profile for this student
    if current_user["role"] == "Student" and current_user["user_id"] != student_id:
        raise HTTPException(status_code=403, detail="Can only create your own profile")
    
    try:
        student = student_crud.create_student_profile(db, student_id, profile_data)
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/students/{student_id}/profile", response_model=StudentOut)
async def update_student_profile(
    student_id: int,
    profile_update: StudentUpdate,
    current_user: Dict[str, Any] = Depends(require_permission("update_student_profiles")),
    db: Session = Depends(get_db)
):
    """Update student profile"""
    student = student_crud.get(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    updated_student = student_crud.update(db, student, profile_update)
    return updated_student

# ==================== FACULTY ENDPOINTS ====================

@app.get("/faculty", response_model=List[FacultyWithUser])
async def get_faculty(
    pagination: Dict = Depends(get_pagination_params),
    dept_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(require_permission("read_departments")),
    db: Session = Depends(get_db)
):
    """Get all faculty"""
    if dept_id:
        faculty = faculty_crud.get_faculty_by_department(db, dept_id, **pagination)
    else:
        faculty = faculty_crud.get_multi(db, **pagination)
    return faculty

@app.get("/faculty/{faculty_id}", response_model=FacultyWithUser)
async def get_faculty_member(
    faculty_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific faculty member"""
    # Check access permissions
    if current_user["user_id"] != faculty_id and current_user["role"] not in ["Admin", "Management"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    faculty = faculty_crud.get_with_user(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty

@app.post("/faculty/{faculty_id}/profile", response_model=FacultyOut)
async def create_faculty_profile(
    faculty_id: int,
    profile_data: FacultyCreate,
    current_user: Dict[str, Any] = Depends(require_role(["Faculty", "Admin"])),
    db: Session = Depends(get_db)
):
    """Create faculty profile"""
    # Check if user can create profile for this faculty
    if current_user["role"] == "Faculty" and current_user["user_id"] != faculty_id:
        raise HTTPException(status_code=403, detail="Can only create your own profile")
    
    try:
        faculty = faculty_crud.create_faculty_profile(db, faculty_id, profile_data)
        return faculty
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== ATTENDANCE ENDPOINTS ====================

@app.get("/attendance/student/{student_id}", response_model=List[AttendanceWithDetails])
async def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student attendance records"""
    # Check access permissions
    if current_user["user_id"] != student_id and current_user["role"] not in ["Faculty", "Admin", "Management", "Parent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to attendance data"
        )
    
    attendance_records = attendance_crud.get_student_attendance(
        db, student_id, start_date, end_date
    )
    return attendance_records

@app.get("/attendance/summary/{student_id}")
async def get_attendance_summary(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance summary for student"""
    # Check access permissions
    if current_user["user_id"] != student_id and current_user["role"] not in ["Faculty", "Admin", "Management", "Parent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to attendance data"
        )
    
    summary = student_crud.get_attendance_summary(db, student_id, start_date, end_date)
    return summary

@app.post("/attendance/mark", response_model=AttendanceOut)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    current_user: Dict[str, Any] = Depends(require_permission("mark_attendance")),
    db: Session = Depends(get_db)
):
    """Mark student attendance"""
    attendance = attendance_crud.mark_attendance(
        db, attendance_data, current_user["user_id"]
    )
    return attendance

@app.post("/attendance/bulk-mark")
async def bulk_mark_attendance(
    session_id: int,
    attendance_records: List[Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(require_permission("mark_attendance")),
    db: Session = Depends(get_db)
):
    """Bulk mark attendance for multiple students"""
    results = attendance_crud.bulk_mark_attendance(
        db, session_id, attendance_records, current_user["user_id"]
    )
    return {"results": results}

# ==================== NOTIFICATION ENDPOINTS ====================

@app.get("/notifications", response_model=List[NotificationOut])
async def get_notifications(
    pagination: Dict = Depends(get_pagination_params),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    notifications = notification_crud.get_notifications_for_user(
        db, current_user["user_id"], models.RoleEnum(current_user["role"]), **pagination
    )
    return notifications

@app.post("/notifications", response_model=NotificationOut)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: Dict[str, Any] = Depends(require_permission("create_notifications")),
    db: Session = Depends(get_db)
):
    """Create new notification"""
    notification = notification_crud.create_notification(
        db, notification_data, current_user["user_id"]
    )
    return notification

# ==================== TIMETABLE ENDPOINTS ====================

@app.get("/timetable/student/{student_id}", response_model=List[TimetableWithDetails])
async def get_student_timetable(
    student_id: int,
    semester_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timetable for student"""
    # Check access permissions
    if current_user["user_id"] != student_id and current_user["role"] not in ["Faculty", "Admin", "Management", "Parent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to timetable data"
        )
    
    timetable = timetable_crud.get_timetable_for_student(db, student_id, semester_id)
    return timetable

@app.get("/timetable/faculty/{faculty_id}", response_model=List[TimetableWithDetails])
async def get_faculty_timetable(
    faculty_id: int,
    semester_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timetable for faculty"""
    # Check access permissions
    if current_user["user_id"] != faculty_id and current_user["role"] not in ["Admin", "Management"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to timetable data"
        )
    
    timetable = timetable_crud.get_timetable_for_faculty(db, faculty_id, semester_id)
    return timetable

# ==================== BULK UPLOAD ENDPOINTS ====================

@app.post("/upload/students", response_model=BulkUploadResponse)
async def bulk_upload_students(
    students_data: List[StudentBulkUpload],
    current_user: Dict[str, Any] = Depends(require_permission("bulk_operations")),
    db: Session = Depends(get_db)
):
    """Bulk upload students from CSV/Excel"""
    results = bulk_upload_crud.bulk_create_students(db, students_data, current_user["user_id"])
    
    return BulkUploadResponse(
        success_count=len(results["success"]),
        error_count=len(results["errors"]),
        errors=results["errors"],
        message=f"Successfully created {len(results['success'])} students, {len(results['errors'])} errors"
    )

@app.post("/upload/faculty", response_model=BulkUploadResponse)
async def bulk_upload_faculty(
    faculty_data: List[FacultyBulkUpload],
    current_user: Dict[str, Any] = Depends(require_permission("bulk_operations")),
    db: Session = Depends(get_db)
):
    """Bulk upload faculty from CSV/Excel"""
    results = bulk_upload_crud.bulk_create_faculty(db, faculty_data, current_user["user_id"])
    
    return BulkUploadResponse(
        success_count=len(results["success"]),
        error_count=len(results["errors"]),
        errors=results["errors"],
        message=f"Successfully created {len(results['success'])} faculty members, {len(results['errors'])} errors"
    )

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/dashboard/student", response_model=StudentDashboard)
async def get_student_dashboard(
    current_student: Student = Depends(get_current_student),
    current_user: Dict[str, Any] = Depends(require_student_role),
    db: Session = Depends(get_db)
):
    """Get student dashboard data"""
    # Get attendance summary
    attendance_summary = student_crud.get_attendance_summary(db, current_student.student_id)
    
    # Get recent notifications
    notifications = notification_crud.get_notifications_for_user(
        db, current_user["user_id"], models.RoleEnum.STUDENT, limit=5
    )
    
    # Get upcoming classes (today's timetable)
    from datetime import date
    timetable = timetable_crud.get_timetable_for_student(db, current_student.student_id)
    today_classes = [t for t in timetable if t.day == date.today().strftime("%A")]
    
    return StudentDashboard(
        user=current_user,
        student=current_student,
        attendance_summary=attendance_summary,
        recent_notifications=notifications,
        upcoming_classes=today_classes
    )

@app.get("/dashboard/faculty", response_model=FacultyDashboard)
async def get_faculty_dashboard(
    current_faculty: Faculty = Depends(get_current_faculty),
    current_user: Dict[str, Any] = Depends(require_faculty_role),
    db: Session = Depends(get_db)
):
    """Get faculty dashboard data"""
    # Get assigned subjects
    subjects = faculty_crud.get_faculty_subjects(db, current_faculty.faculty_id)
    
    # Get recent attendance records
    recent_attendance = attendance_crud.get_multi(db, limit=10)
    
    # Get pending notifications
    notifications = notification_crud.get_notifications_by_faculty(db, current_faculty.faculty_id, limit=5)
    
    return FacultyDashboard(
        user=current_user,
        faculty=current_faculty,
        assigned_subjects=subjects,
        recent_attendance=recent_attendance,
        pending_notifications=notifications
    )

# ==================== UTILITY FUNCTIONS ====================

async def initialize_default_data():
    """Initialize default data for the system"""
    db = SessionLocal()
    try:
        # Check if default data already exists
        existing_admin = user_crud.get_by_email(db, "admin@erp.edu")
        if not existing_admin:
            # Create default admin user
            admin_data = UserCreate(
                name="System Administrator",
                email="admin@erp.edu",
                password="admin123",
                role=RoleEnum.ADMIN,
                department="IT"
            )
            admin_user = user_crud.create_user(db, admin_data)
            print(f"Created default admin user: {admin_user.email}")
        
        # Create default departments
        from crud_v2 import department_crud
        default_departments = [
            {"dept_name": "Computer Science", "dept_code": "CS"},
            {"dept_name": "Information Technology", "dept_code": "IT"},
            {"dept_name": "Electronics", "dept_code": "ECE"},
            {"dept_name": "Mechanical", "dept_code": "ME"},
            {"dept_name": "Civil", "dept_code": "CE"}
        ]
        
        for dept_data in default_departments:
            existing_dept = department_crud.get_by_code(db, dept_data["dept_code"])
            if not existing_dept:
                dept = models.Department(**dept_data)
                db.add(dept)
        
        db.commit()
        print("Default data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing default data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )