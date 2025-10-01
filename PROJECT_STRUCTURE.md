# Project Structure

Complete overview of the ERP System project structure and file organization.

## 📁 Root Directory

```
erp-system/
├── backend/                 # FastAPI backend application
├── frontend/               # React frontend application
├── README.md              # Main documentation
├── QUICKSTART.md          # Quick setup guide
├── API_USAGE_GUIDE.md     # API documentation with examples
├── SCALING_GUIDE.md       # Guide for extending the system
├── DEPLOYMENT_GUIDE.md    # Production deployment guide
├── IMPLEMENTATION_SUMMARY.md  # What was built
└── PROJECT_STRUCTURE.md   # This file
```

## 🔙 Backend Structure

```
backend/
├── api/                           # API layer
│   ├── __init__.py
│   ├── routes/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── student.py            # Student management endpoints
│   │   ├── faculty.py            # Faculty management endpoints
│   │   └── subjects.py           # Subject management endpoints
│   └── middleware/                # Custom middleware
│       ├── __init__.py
│       └── auth.py               # RBAC middleware & permissions
│
├── services/                      # Business logic layer
│   ├── __init__.py
│   ├── user_service.py           # User CRUD and authentication
│   ├── student_service.py        # Student operations & bulk upload
│   ├── faculty_service.py        # Faculty operations
│   ├── attendance_service.py     # Attendance marking & statistics
│   ├── timetable_service.py      # Timetable management
│   ├── notification_service.py   # Notification system
│   └── subject_service.py        # Subject/course management
│
├── config/                        # Configuration management
│   ├── __init__.py
│   └── settings.py               # Pydantic settings (env vars)
│
├── utils/                         # Utility functions
│   ├── __init__.py
│   └── csv_processor.py          # CSV parsing & validation
│
├── migrations/                    # Alembic database migrations
│   ├── env.py                    # Alembic environment config
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration version files
│       └── 001_initial_schema.py # Initial database schema
│
├── seeds/                         # Database seed data
│   └── seed_data.py              # Sample data creation script
│
├── models.py                      # SQLAlchemy database models
├── schemas.py                     # Pydantic validation schemas
├── database.py                    # Database configuration
├── auth.py                        # JWT & password utilities
├── deps.py                        # Legacy dependencies (kept for compatibility)
├── crud.py                        # Legacy CRUD (kept for compatibility)
│
├── main.py                        # Legacy main app (backward compatible)
├── main_new.py                    # New refactored main application
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .env                          # Environment variables (not in git)
├── alembic.ini                   # Alembic configuration
└── setup.py                      # Automated setup script
```

### Backend File Purposes

#### Core Application Files

**main_new.py**
- Modern refactored application entry point
- Includes all new routers
- CORS configuration
- API documentation setup

**models.py**
- SQLAlchemy ORM models
- Database table definitions
- Relationships and constraints
- Indexes for performance

**schemas.py**
- Pydantic models for validation
- Request/response schemas
- Data transfer objects (DTOs)

**database.py**
- Database connection setup
- SQLAlchemy engine configuration
- Session management

**auth.py**
- JWT token creation/verification
- Password hashing/verification
- Security utilities

#### API Layer

**api/routes/auth.py**
- User registration
- Login/logout
- Token verification
- Session management

**api/routes/student.py**
- Student profile operations
- Attendance viewing
- Timetable access
- Notifications
- Admin CRUD operations

**api/routes/faculty.py**
- Faculty profile operations
- Student management
- Attendance marking (single/bulk)
- Timetable creation (single/bulk)
- Notification broadcasting
- CSV bulk upload

**api/routes/subjects.py**
- Subject CRUD operations
- Faculty assignment
- Department filtering

**api/middleware/auth.py**
- JWT authentication
- Role verification
- Permission checking
- Access control decorators

#### Service Layer

**services/user_service.py**
- User creation and updates
- Authentication logic
- User search and filtering

**services/student_service.py**
- Student CRUD operations
- Profile management
- Bulk student creation
- CSV data processing

**services/faculty_service.py**
- Faculty CRUD operations
- Profile management
- Subject assignment

**services/attendance_service.py**
- Attendance marking
- Bulk attendance operations
- Statistics calculation
- Query and filtering

**services/timetable_service.py**
- Timetable entry creation
- Bulk timetable operations
- Conflict detection
- Schedule queries

**services/notification_service.py**
- Notification creation
- Role-based filtering
- Notification management

**services/subject_service.py**
- Subject CRUD
- Faculty assignment
- Department management

#### Configuration & Utils

**config/settings.py**
- Environment variable management
- Application configuration
- Pydantic settings models

**utils/csv_processor.py**
- CSV file parsing
- Data validation
- Template generation
- Error handling

#### Database Management

**migrations/**
- Database version control
- Schema migrations
- Up/down scripts
- Team collaboration

**seeds/seed_data.py**
- Sample data creation
- Initial user accounts
- Demo content
- Development setup

## 🎨 Frontend Structure

```
frontend/
├── public/                        # Static assets
│   └── vite.svg
│
├── src/                           # Source code
│   ├── assets/                   # Images, fonts, etc.
│   │   └── react.svg
│   │
│   ├── components/               # Reusable components
│   │   ├── Navbar.jsx           # Navigation bar
│   │   └── ProtectedRoute.jsx   # Route protection HOC
│   │
│   ├── context/                  # React Context providers
│   │   └── AuthContext.jsx      # Authentication state
│   │
│   ├── pages/                    # Page components
│   │   ├── Login.jsx            # Login page
│   │   ├── Register.jsx         # Registration page
│   │   ├── StudentDashboard.jsx # Student dashboard
│   │   ├── FacultyDashboard.jsx # Faculty dashboard
│   │   ├── Profile.jsx          # Profile management
│   │   ├── Attendance.jsx       # Attendance view
│   │   ├── Timetable.jsx        # Timetable view
│   │   ├── Notifications.jsx    # Notifications view
│   │   └── UnauthorizedPage.jsx # 403 error page
│   │
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Application entry point
│   ├── api.js                    # Axios configuration
│   └── index.css                 # Global styles (TailwindCSS)
│
├── index.html                     # HTML template
├── package.json                   # Node dependencies
├── package-lock.json             # Dependency lock file
├── vite.config.js                # Vite configuration
├── eslint.config.js              # ESLint configuration
├── tailwind.config.js            # TailwindCSS config (if exists)
├── postcss.config.js             # PostCSS config (if exists)
└── README.md                      # Frontend documentation
```

### Frontend File Purposes

#### Core Files

**main.jsx**
- Application entry point
- React rendering
- Initial setup

**App.jsx**
- Main app component
- Route configuration
- Layout structure

**api.js**
- Axios instance configuration
- Request/response interceptors
- Token management

#### Components

**Navbar.jsx**
- Navigation menu
- Role-based links
- User info display
- Logout functionality

**ProtectedRoute.jsx**
- Route protection wrapper
- Role verification
- Redirect logic

#### Context

**AuthContext.jsx**
- Authentication state
- User information
- Login/logout functions
- Token management

#### Pages

**Login.jsx**
- Login form
- Authentication
- Error handling

**StudentDashboard.jsx**
- Student overview
- Quick stats
- Recent notifications

**FacultyDashboard.jsx**
- Faculty overview
- Student management
- Quick actions

**Profile.jsx**
- Profile viewing
- Profile editing
- Role-specific fields

**Attendance.jsx**
- Attendance records
- Filtering
- Statistics (student)
- Marking interface (faculty)

**Timetable.jsx**
- Schedule display
- Day filtering
- Subject details

**Notifications.jsx**
- Notification list
- Priority indicators
- Creation (faculty)

## 🗄️ Database Schema

### Tables Overview

```
Users
├── user_id (PK)
├── name
├── email (unique)
├── password_hash
├── role (enum)
├── department
├── phone
├── address
├── is_active
├── created_at
└── updated_at

Students
├── student_id (PK, FK → Users)
├── roll_no (unique)
├── class_name
├── year
├── section
├── division
├── batch
└── admission_date

Faculty
├── faculty_id (PK, FK → Users)
├── employee_id (unique)
├── designation
├── dept
├── specialization
└── joining_date

Subjects
├── subject_id (PK)
├── subject_code (unique)
├── subject_name
├── faculty_id (FK → Faculty)
├── semester
├── credits
├── department
└── created_at

Attendance
├── attendance_id (PK)
├── student_id (FK → Students)
├── subject_id (FK → Subjects)
├── date
├── status
├── marked_by (FK → Faculty)
├── remarks
├── created_at
└── updated_at

Timetable
├── timetable_id (PK)
├── subject_id (FK → Subjects)
├── student_id (FK → Students)
├── day
├── time_slot
├── room_number
├── semester
├── academic_year
└── created_at

Notifications
├── notification_id (PK)
├── title
├── description
├── created_by (FK → Faculty)
├── visible_to
├── priority
├── is_active
├── created_at
└── updated_at
```

## 🔄 Request Flow

### Authentication Flow
```
Client → POST /api/auth/login
    ↓
auth.py router → UserService.authenticate_user()
    ↓
Database query → Verify credentials
    ↓
Generate JWT token
    ↓
Return token to client
```

### Protected Resource Flow
```
Client → GET /api/students/me (with token)
    ↓
auth middleware → Verify JWT token
    ↓
Extract user from token
    ↓
Check role permissions
    ↓
student.py router → StudentService.get_student_by_id()
    ↓
Database query
    ↓
Return data to client
```

### Bulk Operation Flow
```
Client → POST /api/faculty/students/bulk-upload (CSV)
    ↓
faculty.py router → CSVProcessor.parse_student_csv()
    ↓
Validate each row
    ↓
StudentService.bulk_create_students()
    ↓
Create users + student profiles in transaction
    ↓
Return success/error report
```

## 📦 Dependencies

### Backend Dependencies
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **pymysql** - MySQL driver
- **pydantic** - Data validation
- **pydantic-settings** - Configuration
- **PyJWT** - JWT tokens
- **passlib** - Password hashing
- **alembic** - Database migrations
- **python-multipart** - File uploads
- **email-validator** - Email validation

### Frontend Dependencies
- **react** - UI library
- **react-dom** - React renderer
- **react-router-dom** - Routing
- **axios** - HTTP client
- **tailwindcss** - CSS framework
- **vite** - Build tool

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEBUG=False
ALLOWED_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 🚀 Startup Commands

### Development
```bash
# Backend
cd backend
uvicorn main_new:app --reload

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Backend
gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ folder with nginx/apache
```

## 📊 Code Statistics

- **Backend Files**: 25+
- **Frontend Files**: 15+
- **Database Tables**: 7
- **API Endpoints**: 50+
- **Service Functions**: 100+
- **Documentation Pages**: 6
- **Lines of Code**: 5000+
- **Lines of Documentation**: 2000+

## 🎯 Key Design Principles

1. **Separation of Concerns** - Routes, Services, Models separate
2. **DRY (Don't Repeat Yourself)** - Reusable services
3. **SOLID Principles** - Clean, maintainable code
4. **RESTful Design** - Standard API patterns
5. **Security First** - RBAC, validation, encryption
6. **Documentation Driven** - Every feature documented

---

This structure supports scalability, maintainability, and ease of understanding for developers joining the project.
