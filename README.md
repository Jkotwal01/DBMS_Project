# ERP System - Scalable Role-Based Access Control

A comprehensive full-stack ERP system built with FastAPI (Python) and React (Vite + TailwindCSS) featuring robust role-based access control, student management, attendance tracking, timetable management, and notification system.

## 🌟 Features

### Role-Based Access Control (RBAC)
- **Extensible Role System**: Student, Faculty, Admin, Parent, Management (easily add new roles)
- **Permission-Based Access**: Fine-grained control over what each role can access
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Protected Routes**: Both backend and frontend route protection

### Student Portal
- ✅ View personal attendance records with statistics
- ✅ Access personalized timetable
- ✅ Receive notifications from faculty
- ✅ Edit own profile information
- ✅ Filter attendance by subject and date range

### Faculty Portal
- ✅ Manage student profiles (Create, Read, Update, Delete)
- ✅ Mark attendance (individual and bulk)
- ✅ Upload students via CSV (bulk import)
- ✅ Create and manage timetables
- ✅ Send notifications to students/faculty
- ✅ View assigned subjects and classes
- ✅ Update own profile

### Admin Features (Future)
- Manage all users (students, faculty)
- System-wide reporting
- Configure roles and permissions
- Manage subjects and departments

## 🏗️ Architecture

### Backend (Clean Architecture)
```
backend/
├── api/
│   ├── routes/          # API endpoints
│   │   ├── auth.py      # Authentication routes
│   │   ├── student.py   # Student operations
│   │   ├── faculty.py   # Faculty operations
│   │   └── subjects.py  # Subject management
│   └── middleware/      # Custom middleware
│       └── auth.py      # RBAC middleware
├── services/            # Business logic layer
│   ├── user_service.py
│   ├── student_service.py
│   ├── faculty_service.py
│   ├── attendance_service.py
│   ├── timetable_service.py
│   ├── notification_service.py
│   └── subject_service.py
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # Database configuration
├── auth.py              # Authentication utilities
├── config/              # Configuration
│   └── settings.py      # Application settings
├── utils/               # Utility functions
│   └── csv_processor.py # CSV file processing
├── migrations/          # Alembic migrations
│   └── versions/
└── seeds/               # Seed data
    └── seed_data.py
```

### Frontend (Component-Based)
```
frontend/
├── src/
│   ├── components/      # Reusable components
│   ├── pages/           # Page components
│   ├── context/         # React Context (Auth, etc.)
│   ├── services/        # API service layer
│   └── utils/           # Utility functions
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL database:**
   ```sql
   CREATE DATABASE attendance_db;
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/attendance_db
   SECRET_KEY=your-super-secret-key-change-this
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ```

6. **Run database migrations (optional - tables auto-create):**
   ```bash
   alembic upgrade head
   ```

7. **Seed the database with sample data:**
   ```bash
   python seeds/seed_data.py
   ```

8. **Start the backend server:**
   ```bash
   # Using the new refactored main file
   uvicorn main_new:app --reload --host 0.0.0.0 --port 8000
   
   # Or using the old main file (backward compatible)
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend runs at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (if needed):**
   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

   Frontend runs at: http://localhost:5173

## 🔑 Default Login Credentials

After running the seed script, you can login with these accounts:

### Faculty Accounts
```
Email: john.smith@university.edu
Password: faculty123
Role: Professor (Computer Science)

Email: sarah.johnson@university.edu
Password: faculty123
Role: Associate Professor (Mathematics)

Email: michael.brown@university.edu
Password: faculty123
Role: Assistant Professor (Physics)
```

### Student Accounts
```
Email: alice.williams@student.edu
Password: student123
Roll No: CS2024001

Email: bob.davis@student.edu
Password: student123
Roll No: CS2024002

Email: carol.martinez@student.edu
Password: student123
Roll No: CS2024003

... and more (check seed_data.py)
```

## 📚 API Documentation

After starting the backend server:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key API Endpoints

#### Authentication
```
POST   /api/auth/register     - Register new user
POST   /api/auth/login        - Login and get JWT token
GET    /api/auth/me           - Get current user info
POST   /api/auth/logout       - Logout (client-side)
```

#### Students
```
GET    /api/students/me                    - Get my profile
PUT    /api/students/me/profile            - Update my profile
GET    /api/students/me/attendance         - Get my attendance
GET    /api/students/me/attendance/stats   - Get attendance statistics
GET    /api/students/me/timetable          - Get my timetable
GET    /api/students/me/notifications      - Get my notifications

# Faculty/Admin only
GET    /api/students/                      - Get all students
POST   /api/students/                      - Create student
GET    /api/students/{id}                  - Get student by ID
PUT    /api/students/{id}                  - Update student
DELETE /api/students/{id}                  - Delete student
```

#### Faculty
```
GET    /api/faculty/me                     - Get my profile
PUT    /api/faculty/me/profile             - Update my profile
GET    /api/faculty/me/subjects            - Get my subjects

# Attendance Management
POST   /api/faculty/attendance             - Mark attendance
POST   /api/faculty/attendance/bulk        - Bulk mark attendance
GET    /api/faculty/attendance/subject/{id} - Get subject attendance
DELETE /api/faculty/attendance/{id}        - Delete attendance

# Timetable Management
POST   /api/faculty/timetable              - Create timetable entry
POST   /api/faculty/timetable/bulk         - Bulk create timetable
DELETE /api/faculty/timetable/{id}         - Delete timetable entry

# Notification Management
POST   /api/faculty/notifications          - Create notification
GET    /api/faculty/notifications          - Get my notifications
DELETE /api/faculty/notifications/{id}     - Delete notification

# Student Management
POST   /api/faculty/students/bulk-upload   - Bulk upload students (CSV)
GET    /api/faculty/students/csv-template  - Get CSV template

# Faculty CRUD (Admin)
GET    /api/faculty/                       - Get all faculty
POST   /api/faculty/                       - Create faculty
GET    /api/faculty/{id}                   - Get faculty by ID
```

#### Subjects
```
GET    /api/subjects/        - Get all subjects
POST   /api/subjects/        - Create subject
GET    /api/subjects/{id}    - Get subject by ID
PUT    /api/subjects/{id}    - Update subject
DELETE /api/subjects/{id}    - Delete subject
```

## 🔐 Security Features

1. **Password Hashing**: Bcrypt with automatic salt generation
2. **JWT Tokens**: Secure token-based authentication
3. **Role-Based Access**: Middleware enforces role requirements
4. **Permission System**: Fine-grained permission control
5. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
6. **CORS Protection**: Configured allowed origins
7. **Input Validation**: Pydantic schema validation

## 📊 Database Schema

### Core Tables
- **users**: Base user information for all roles
- **students**: Student-specific profile data
- **faculty**: Faculty-specific profile data
- **subjects**: Course/subject information
- **attendance**: Attendance records with audit trail
- **timetable**: Student timetable entries
- **notifications**: Announcement system

### Key Relationships
- User → Student (1:1)
- User → Faculty (1:1)
- Faculty → Subject (1:N)
- Faculty → Notification (1:N)
- Student → Attendance (1:N)
- Subject → Attendance (1:N)
- Student → Timetable (1:N)

## 🔄 Bulk Operations

### Bulk Student Upload

Faculty can upload students via CSV file:

1. Get CSV template: `GET /api/faculty/students/csv-template`
2. Fill in student data:
   ```csv
   name,email,password,roll_no,class_name,year,section,division,batch,department,phone,address
   John Doe,john@student.edu,student123,CS2024001,Computer Science,2,A,1,2024,CS,1234567890,123 Main St
   ```
3. Upload: `POST /api/faculty/students/bulk-upload`

### Bulk Attendance Marking

Mark attendance for multiple students at once:
```json
POST /api/faculty/attendance/bulk
{
  "subject_id": 1,
  "date": "2024-03-15",
  "attendance_list": [
    {"student_id": 1, "status": "Present"},
    {"student_id": 2, "status": "Absent"},
    {"student_id": 3, "status": "Late"}
  ]
}
```

### Bulk Timetable Creation

Create timetable entries for multiple students:
```json
POST /api/faculty/timetable/bulk
{
  "subject_id": 1,
  "day": "Monday",
  "time_slot": "09:00-10:00",
  "room_number": "Room 101",
  "semester": 3,
  "academic_year": "2024-2025",
  "student_ids": [1, 2, 3, 4, 5]
}
```

## 🎯 Extending the System

### Adding a New Role

1. **Update models.py** - Add role to RoleEnum:
   ```python
   class RoleEnum(str, enum.Enum):
       Student = "Student"
       Faculty = "Faculty"
       Admin = "Admin"
       Parent = "Parent"        # NEW
       Management = "Management" # NEW
   ```

2. **Create role-specific model** (if needed):
   ```python
   class Parent(Base):
       __tablename__ = "parents"
       parent_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
       student_id = Column(Integer, ForeignKey("students.student_id"))
       # ... additional fields
   ```

3. **Update RBAC middleware** - Add permissions:
   ```python
   ROLE_PERMISSIONS = {
       "Parent": [
           Permission.VIEW_CHILD_ATTENDANCE,
           Permission.VIEW_CHILD_TIMETABLE,
           # ... more permissions
       ]
   }
   ```

4. **Create service layer** - `services/parent_service.py`

5. **Create API routes** - `api/routes/parent.py`

6. **Update main.py** - Include router:
   ```python
   from api.routes import parent
   app.include_router(parent.router)
   ```

7. **Create frontend components** - Add parent dashboard, routes, etc.

### Adding a New Permission

1. **Define permission** in `api/middleware/auth.py`:
   ```python
   class Permission:
       VIEW_REPORTS = "view_reports"
   ```

2. **Assign to roles**:
   ```python
   ROLE_PERMISSIONS = {
       "Admin": [Permission.VIEW_REPORTS, ...]
   }
   ```

3. **Use in routes**:
   ```python
   @router.get("/reports", dependencies=[Depends(require_permission(Permission.VIEW_REPORTS))])
   def get_reports():
       ...
   ```

## 🧪 Testing

### Manual Testing with Swagger
1. Start backend server
2. Go to http://localhost:8000/api/docs
3. Click "Authorize" and login with credentials
4. Test endpoints interactively

### Testing CSV Upload
1. Download template from `/api/faculty/students/csv-template`
2. Fill with test data
3. Upload via `/api/faculty/students/bulk-upload`

## 📈 Production Deployment

### Backend
1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY`
3. Configure proper database credentials
4. Use production ASGI server (Gunicorn + Uvicorn workers):
   ```bash
   gunicorn main_new:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend
1. Build production bundle:
   ```bash
   npm run build
   ```
2. Serve static files with Nginx or deploy to Vercel/Netlify

### Database
1. Run migrations in production:
   ```bash
   alembic upgrade head
   ```
2. Set up regular backups
3. Enable SSL connections

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.115.0
- **ORM**: SQLAlchemy 2.0.34
- **Database**: MySQL 8.0 (via PyMySQL)
- **Authentication**: JWT (PyJWT 2.9.0)
- **Password Hashing**: Passlib with bcrypt
- **Migrations**: Alembic 1.13.2
- **Validation**: Pydantic 2.x

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React Context

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at `/api/docs`
- Review this README

## 🔮 Future Enhancements

- [ ] Add Admin dashboard
- [ ] Parent portal for viewing child's progress
- [ ] Management portal for reports and analytics
- [ ] Email notifications
- [ ] SMS integration
- [ ] Real-time updates with WebSockets
- [ ] Mobile app (React Native)
- [ ] Advanced reporting and analytics
- [ ] Exam management system
- [ ] Fee management
- [ ] Library management
- [ ] Hostel management

## ⚙️ Configuration

All configurations are in `backend/config/settings.py` and can be overridden via environment variables in `.env` file.

---

**Built with ❤️ for educational institutions**
