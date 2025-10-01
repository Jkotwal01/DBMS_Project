# Enhanced ERP System

A scalable Educational Resource Planning (ERP) system built with FastAPI (backend) and React (frontend) featuring comprehensive role-based access control (RBAC).

## 🚀 Features

### Core Functionality
- **Multi-role Authentication**: Student, Faculty, Admin, Parent, Management
- **Role-based Access Control**: Fine-grained permissions system
- **Audit Logging**: Complete activity tracking
- **Bulk Operations**: CSV upload for student data
- **Real-time Notifications**: Priority-based messaging system
- **Grade Management**: Comprehensive academic record keeping
- **Attendance Tracking**: Detailed attendance monitoring
- **Timetable Management**: Dynamic schedule management

### Security Features
- JWT-based authentication
- Password hashing with bcrypt
- Session management
- IP tracking and user agent logging
- Account deactivation capabilities

### Scalability Features
- Database migrations with Alembic
- Modular architecture
- Extensible permission system
- System settings management
- Health monitoring

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── alembic/                 # Database migrations
├── main_enhanced.py         # Enhanced API endpoints
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── crud.py                 # Database operations
├── auth.py                 # Authentication logic
├── deps.py                 # Dependencies & middleware
├── database.py             # Database configuration
├── seed_data.py            # Initial data seeding
└── requirements.txt        # Python dependencies
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/         # Reusable components
│   ├── pages/             # Page components
│   ├── context/           # React context
│   ├── api.js             # API client
│   └── App.jsx            # Main app component
├── package.json           # Node dependencies
└── vite.config.js         # Vite configuration
```

### Database Schema
```
Users (Core user table)
├── Students (Student profiles)
├── Faculty (Faculty profiles)
├── Admins (Admin profiles)
└── Parents (Parent profiles)

Academic Management
├── Subjects (Course catalog)
├── Grades (Academic records)
├── Attendance (Attendance tracking)
└── Timetable (Schedule management)

System Management
├── Permissions (Access control)
├── UserPermissions (User-permission mapping)
├── Notifications (Messaging system)
├── AuditLogs (Activity tracking)
└── SystemSettings (Configuration)
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd erp-system/backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup MySQL database**
```bash
# Start MySQL service
sudo systemctl start mysql

# Create database user
mysql -u root -p
CREATE USER 'erp_user'@'localhost' IDENTIFIED BY 'erp_password';
GRANT ALL PRIVILEGES ON *.* TO 'erp_user'@'localhost';
FLUSH PRIVILEGES;
CREATE DATABASE attendance_db;
EXIT;
```

4. **Run database migrations**
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Run migrations
alembic upgrade head
```

5. **Seed initial data**
```bash
python3 seed_data.py
# or use the simple user creation script
python3 create_users.py
```

6. **Start the backend server**
```bash
python3 main_enhanced.py
# or
uvicorn main_enhanced:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 👥 Default User Accounts

After running the seed script, you can login with these accounts:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@erp.edu | admin123 | System Administrator |
| Faculty | john.smith@erp.edu | faculty123 | Computer Science Professor |
| Student | alice.brown@student.erp.edu | student123 | CS Student |

## 🔐 Role-Based Access Control

### Student Role
- ✅ View own profile and update basic info
- ✅ View own attendance records
- ✅ View own grades
- ✅ View timetable
- ✅ View notifications
- ❌ Cannot access other students' data
- ❌ Cannot modify system data

### Faculty Role
- ✅ All Student permissions for own profile
- ✅ View and manage assigned students
- ✅ Mark attendance for assigned subjects
- ✅ Create and manage grades
- ✅ Create notifications
- ✅ Manage timetable for assigned subjects
- ✅ View faculty-specific notifications
- ❌ Cannot access admin functions

### Admin Role
- ✅ All system permissions
- ✅ User management (create, update, deactivate)
- ✅ Bulk operations
- ✅ System settings management
- ✅ Audit log access
- ✅ Full CRUD on all entities
- ✅ Permission management

## 📊 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /auth/me` - Get current user
- `POST /logout` - User logout

### User Management
- `GET /users` - List users (Admin/Faculty)
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user (Admin)
- `DELETE /users/{id}` - Deactivate user (Admin)

### Student Management
- `GET /students` - List students
- `GET /students/{id}` - Get student details
- `PUT /students/{id}` - Update student
- `POST /students/bulk-upload` - Bulk upload via CSV

### Faculty Management
- `GET /faculty` - List faculty
- `PUT /faculty/{id}` - Update faculty profile
- `GET /faculty/classes` - Get assigned classes

### Academic Management
- `POST /faculty/attendance` - Mark attendance
- `GET /faculty/attendance/{subject_id}` - Get subject attendance
- `POST /faculty/grades` - Create grade
- `GET /faculty/grades/{subject_id}` - Get subject grades

### Subject Management
- `GET /subjects` - List subjects
- `POST /subjects` - Create subject
- `PUT /subjects/{id}` - Update subject

### Notifications
- `GET /notifications` - Get user notifications
- `POST /faculty/notifications` - Create notification
- `PUT /notifications/{id}/read` - Mark as read

### Admin Functions
- `GET /admin/dashboard` - Dashboard stats
- `GET /admin/audit-logs` - System audit logs
- `GET /admin/system-settings` - System configuration

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
DATABASE_URL=mysql+pymysql://erp_user:erp_password@localhost:3306/attendance_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
```

### System Settings
Configurable via Admin panel:
- Academic year
- Current semester
- Attendance threshold
- Session timeout
- Maximum login attempts

## 🚀 Deployment

### Production Deployment

1. **Backend (FastAPI)**
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main_enhanced:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Frontend (React)**
```bash
# Build for production
npm run build

# Serve with nginx or any static file server
```

3. **Database**
- Use managed MySQL service (AWS RDS, Google Cloud SQL)
- Set up proper backup strategies
- Configure SSL connections

4. **Security**
- Use HTTPS in production
- Set strong SECRET_KEY
- Configure CORS properly
- Set up rate limiting
- Use environment variables for secrets

## 📈 Scaling the System

### Adding New Roles

1. **Update the RoleEnum in models.py**
```python
class RoleEnum(str, enum.Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"
    NEW_ROLE = "NewRole"  # Add here
```

2. **Create role-specific model (if needed)**
```python
class NewRole(Base):
    __tablename__ = "new_roles"
    new_role_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    # Add role-specific fields
```

3. **Add permissions for the new role**
```python
# In seed_data.py or via admin panel
permissions = [
    {"name": "new_role_permission", "resource": "resource", "action": "action"}
]
```

4. **Create role-specific endpoints**
```python
@app.get("/new-role/dashboard")
def new_role_dashboard(
    current_user: models.User = Depends(require_role("NewRole")),
    db: Session = Depends(get_db)
):
    # Role-specific logic
    pass
```

### Adding New Features

1. **Database Changes**
   - Create migration: `alembic revision --autogenerate -m "Description"`
   - Apply migration: `alembic upgrade head`

2. **API Changes**
   - Add new schemas in `schemas.py`
   - Add CRUD operations in `crud.py`
   - Add endpoints in `main_enhanced.py`

3. **Frontend Changes**
   - Add new components
   - Update routing
   - Add API calls

## 🧪 Testing

### Backend Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Frontend Testing
```bash
# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## 📝 API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the audit logs for debugging

## 🔄 Version History

### v2.0.0 (Current)
- Enhanced RBAC system
- Audit logging
- Bulk operations
- System settings
- Improved security

### v1.0.0
- Basic student-faculty system
- Simple authentication
- Basic CRUD operations