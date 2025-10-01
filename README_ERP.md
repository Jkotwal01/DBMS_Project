# ERP Attendance Management System

A comprehensive Enterprise Resource Planning (ERP) system for educational institutions with role-based access control, built with FastAPI (Python) and React (JavaScript).

## 🚀 Features

### Core Features
- **Role-Based Access Control (RBAC)** with 5 user roles
- **Secure Authentication** with JWT tokens
- **Attendance Management** with real-time tracking
- **Timetable Management** with scheduling
- **Notification System** with targeted messaging
- **Bulk Data Upload** (CSV/Excel support)
- **Audit Logging** for security and compliance
- **Responsive Design** with modern UI/UX

### User Roles

#### 1. **Student**
- View personal attendance records
- Access timetable and class schedules
- Receive and view notifications
- Manage personal profile
- View academic progress

#### 2. **Faculty**
- Mark student attendance
- Manage assigned subjects and classes
- Send notifications to students
- View and update student profiles
- Upload bulk student data
- Create and manage timetables

#### 3. **Admin**
- Full system administration
- User management (create, update, delete)
- Department and subject management
- System settings and configuration
- Bulk operations and data management
- Audit log access

#### 4. **Parent**
- View child's attendance and academic progress
- Receive notifications about child
- Access child's timetable
- Limited profile management

#### 5. **Management**
- View analytics and reports
- Department oversight
- Financial data access
- Strategic reporting

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── models_v2.py          # Enhanced database models
├── schemas_v2.py         # Pydantic schemas
├── crud_v2.py           # Database operations
├── auth_v2.py           # Authentication & RBAC
├── deps_v2.py           # Dependencies & middleware
├── main_v2.py           # Main application
├── database.py          # Database configuration
├── migrations/          # Database migrations
├── seed_data.py         # Initial data seeding
└── requirements.txt     # Python dependencies
```

### Frontend (React + Tailwind CSS)
```
frontend/
├── src/
│   ├── components/
│   │   ├── NavbarV2.jsx           # Enhanced navigation
│   │   └── ProtectedRouteV2.jsx   # Role-based routing
│   ├── pages/
│   │   ├── StudentDashboardV2.jsx # Student interface
│   │   └── FacultyDashboardV2.jsx # Faculty interface
│   ├── context/
│   │   └── AuthContext.jsx        # Authentication context
│   └── api.js                     # API client
├── package.json
└── vite.config.js
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd erp-attendance-system
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the backend directory:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/erp_attendance
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

4. **Set up MySQL database**
```sql
CREATE DATABASE erp_attendance;
CREATE USER 'erp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON erp_attendance.* TO 'erp_user'@'localhost';
FLUSH PRIVILEGES;
```

5. **Run database migrations**
```bash
# Create migration
python -m alembic revision --autogenerate -m "Initial migration"

# Apply migrations
python -m alembic upgrade head
```

6. **Seed initial data**
```bash
python seed_data.py
```

7. **Start the backend server**
```bash
python main_v2.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📊 Database Schema

### Core Tables

#### Users & Authentication
- `users` - Base user information
- `login_logs` - Authentication tracking
- `audit_logs` - System activity logging

#### Academic Structure
- `departments` - Academic departments
- `academic_years` - Academic year management
- `semesters` - Semester tracking
- `subjects` - Course/subject management

#### User Profiles
- `students` - Student-specific information
- `faculty` - Faculty-specific information
- `admins` - Admin-specific information
- `parents` - Parent information
- `parent_students` - Parent-student relationships

#### Academic Operations
- `enrollments` - Student subject enrollments
- `timetable` - Class scheduling
- `attendance_sessions` - Attendance session tracking
- `attendance` - Individual attendance records

#### Communication
- `notifications` - System notifications
- `file_uploads` - File management

## 🔐 Security Features

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration management
- Refresh token support

### Authorization
- Role-based access control (RBAC)
- Permission-based access control
- Resource-level authorization
- API endpoint protection

### Audit & Compliance
- Comprehensive audit logging
- Login attempt tracking
- User activity monitoring
- Data change tracking

## 🚀 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Current user info
- `POST /auth/logout` - User logout

### User Management
- `GET /users` - List users (Admin)
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user (Admin)

### Student Operations
- `GET /students` - List students
- `GET /students/{id}` - Student details
- `POST /students/{id}/profile` - Create student profile
- `PUT /students/{id}/profile` - Update student profile

### Faculty Operations
- `GET /faculty` - List faculty
- `GET /faculty/{id}` - Faculty details
- `POST /faculty/{id}/profile` - Create faculty profile
- `PUT /faculty/{id}/profile` - Update faculty profile

### Attendance Management
- `GET /attendance/student/{id}` - Student attendance
- `GET /attendance/summary/{id}` - Attendance summary
- `POST /attendance/mark` - Mark attendance
- `POST /attendance/bulk-mark` - Bulk attendance marking

### Notification System
- `GET /notifications` - User notifications
- `POST /notifications` - Create notification
- `PUT /notifications/{id}` - Update notification

### Dashboard
- `GET /dashboard/student` - Student dashboard data
- `GET /dashboard/faculty` - Faculty dashboard data

### Bulk Operations
- `POST /upload/students` - Bulk student upload
- `POST /upload/faculty` - Bulk faculty upload

## 🎨 Frontend Features

### Role-Based UI
- Dynamic navigation based on user role
- Role-specific dashboard layouts
- Permission-based component rendering
- Responsive design for all devices

### Enhanced Dashboards
- Real-time statistics and metrics
- Interactive charts and graphs
- Quick action buttons
- Recent activity feeds

### User Experience
- Modern, clean interface
- Intuitive navigation
- Loading states and error handling
- Form validation and feedback

## 🔧 Development

### Adding New Roles

1. **Update Backend Models**
```python
# In models_v2.py
class RoleEnum(str, enum.Enum):
    STUDENT = "Student"
    FACULTY = "Faculty"
    ADMIN = "Admin"
    PARENT = "Parent"
    MANAGEMENT = "Management"
    NEW_ROLE = "NewRole"  # Add new role
```

2. **Update Permissions**
```python
# In auth_v2.py
ROLE_PERMISSIONS = {
    "NewRole": [
        "permission1",
        "permission2",
        # Add permissions
    ]
}
```

3. **Create Role-Specific Models**
```python
# In models_v2.py
class NewRole(Base):
    __tablename__ = "new_roles"
    # Define role-specific fields
```

4. **Update Frontend**
```javascript
// In NavbarV2.jsx
case 'newrole':
    return [
        { path: '/newrole/dashboard', label: 'Dashboard', icon: '🏠' },
        // Add navigation items
    ];
```

### Adding New Features

1. **Backend Development**
   - Create new models in `models_v2.py`
   - Add schemas in `schemas_v2.py`
   - Implement CRUD operations in `crud_v2.py`
   - Create API endpoints in `main_v2.py`

2. **Frontend Development**
   - Create new components in `src/components/`
   - Add new pages in `src/pages/`
   - Update routing in `App.jsx`
   - Add navigation items in `NavbarV2.jsx`

### Database Migrations

```bash
# Create new migration
python -m alembic revision --autogenerate -m "Add new feature"

# Apply migration
python -m alembic upgrade head

# Rollback migration
python -m alembic downgrade -1
```

## 🧪 Testing

### Backend Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Frontend Testing
```bash
# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

## 📈 Performance & Monitoring

### Backend Monitoring
- Request/response logging
- Database query optimization
- Memory usage tracking
- Error rate monitoring

### Frontend Performance
- Code splitting and lazy loading
- Image optimization
- Bundle size monitoring
- Performance metrics

## 🔒 Security Best Practices

### Backend Security
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting
- Secure headers

### Frontend Security
- XSS prevention
- Secure API communication
- Input validation
- Secure storage practices

## 🚀 Deployment

### Backend Deployment
1. Set up production database
2. Configure environment variables
3. Run database migrations
4. Deploy with Gunicorn or similar
5. Set up reverse proxy (Nginx)

### Frontend Deployment
1. Build production bundle
2. Deploy to static hosting (Vercel, Netlify)
3. Configure environment variables
4. Set up CDN for assets

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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
- Check the documentation
- Review the API documentation

## 🎯 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced analytics and reporting
- [ ] Integration with external systems
- [ ] Multi-language support
- [ ] Advanced notification system
- [ ] Real-time collaboration features
- [ ] Advanced search and filtering
- [ ] Data export capabilities
- [ ] Integration with learning management systems

---

**Built with ❤️ for educational institutions worldwide**