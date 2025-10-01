# Enhanced ERP System - Project Structure

## 📁 Complete Directory Structure

```
enhanced-erp-system/
├── 📄 README.md                    # Main documentation
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 🔧 setup.sh                     # Automated setup script
├── 🚀 start_backend.sh             # Backend startup script
├── 🚀 start_frontend.sh            # Frontend startup script
│
├── 📂 backend/                      # FastAPI Backend
│   ├── 📂 alembic/                 # Database migrations
│   │   ├── 📂 versions/            # Migration files
│   │   ├── 📄 env.py               # Alembic environment
│   │   ├── 📄 script.py.mako       # Migration template
│   │   └── 📄 README               # Alembic readme
│   │
│   ├── 📄 alembic.ini              # Alembic configuration
│   ├── 📄 main_enhanced.py         # Enhanced API endpoints
│   ├── 📄 main.py                  # Original API (legacy)
│   ├── 📄 models.py                # SQLAlchemy database models
│   ├── 📄 schemas.py               # Pydantic request/response schemas
│   ├── 📄 crud.py                  # Database CRUD operations
│   ├── 📄 auth.py                  # Authentication & JWT handling
│   ├── 📄 deps.py                  # FastAPI dependencies & middleware
│   ├── 📄 database.py              # Database connection & configuration
│   ├── 📄 seed_data.py             # Database seeding script
│   ├── 📄 create_users.py          # Simple user creation script
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 sample_students.csv      # Sample CSV for bulk upload
│   └── 📄 .env                     # Environment variables (created by setup)
│
└── 📂 frontend/                     # React Frontend
    ├── 📂 public/                   # Static assets
    │   ├── 📄 vite.svg              # Vite logo
    │   └── 📄 index.html            # HTML template
    │
    ├── 📂 src/                      # Source code
    │   ├── 📂 components/           # Reusable React components
    │   │   ├── 📄 Navbar.jsx        # Navigation component
    │   │   └── 📄 ProtectedRoute.jsx # Route protection
    │   │
    │   ├── 📂 context/              # React Context providers
    │   │   └── 📄 AuthContext.jsx   # Authentication context
    │   │
    │   ├── 📂 pages/                # Page components
    │   │   ├── 📄 Login.jsx         # Login page
    │   │   ├── 📄 Register.jsx      # Registration page
    │   │   ├── 📄 StudentDashboard.jsx    # Student dashboard
    │   │   ├── 📄 FacultyDashboard.jsx    # Faculty dashboard
    │   │   ├── 📄 Profile.jsx       # Profile management
    │   │   ├── 📄 Attendance.jsx    # Attendance views
    │   │   ├── 📄 Timetable.jsx     # Timetable display
    │   │   ├── 📄 Notifications.jsx # Notifications page
    │   │   └── 📄 UnauthorizedPage.jsx # 403 error page
    │   │
    │   ├── 📂 assets/               # Static assets
    │   │   └── 📄 react.svg         # React logo
    │   │
    │   ├── 📄 App.jsx               # Main application component
    │   ├── 📄 main.jsx              # Application entry point
    │   ├── 📄 index.css             # Global styles
    │   └── 📄 api.js                # API client configuration
    │
    ├── 📄 package.json              # Node.js dependencies & scripts
    ├── 📄 package-lock.json         # Dependency lock file
    ├── 📄 vite.config.js            # Vite configuration
    ├── 📄 eslint.config.js          # ESLint configuration
    └── 📄 README.md                 # Frontend-specific readme
```

## 🏗️ Architecture Overview

### Backend Architecture (FastAPI)

#### Core Components
- **main_enhanced.py**: Enhanced API with comprehensive endpoints
- **models.py**: Database models with relationships
- **schemas.py**: Request/response validation schemas
- **crud.py**: Database operations and business logic
- **auth.py**: JWT authentication and password hashing
- **deps.py**: Dependency injection and middleware

#### Database Layer
- **SQLAlchemy ORM**: Object-relational mapping
- **Alembic**: Database migrations and versioning
- **MySQL**: Primary database storage

#### Security Features
- JWT token-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Audit logging for all operations
- IP tracking and session management

### Frontend Architecture (React)

#### Component Structure
- **Pages**: Full-page components for different views
- **Components**: Reusable UI components
- **Context**: Global state management
- **API Client**: Centralized API communication

#### Routing & Protection
- React Router for navigation
- Protected routes based on user roles
- Automatic redirects based on authentication state

## 📊 Database Schema

### Core Tables

#### Users Table
```sql
users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM('Student', 'Faculty', 'Admin', 'Parent', 'Management'),
    department VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

#### Role-Specific Tables
- **students**: Student profiles and academic info
- **faculty**: Faculty profiles and employment details
- **admins**: Administrative user profiles
- **parents**: Parent/guardian information

#### Academic Tables
- **subjects**: Course catalog and subject details
- **grades**: Academic performance records
- **attendance**: Daily attendance tracking
- **timetable**: Class scheduling information

#### System Tables
- **permissions**: Available system permissions
- **user_permissions**: User-permission mappings
- **notifications**: System messaging
- **audit_logs**: Activity tracking
- **system_settings**: Configuration management

## 🔐 Security Implementation

### Authentication Flow
1. User submits credentials via login form
2. Backend validates credentials against database
3. JWT token generated with user info and expiration
4. Token stored in frontend localStorage
5. Token included in all subsequent API requests
6. Backend validates token on each request

### Authorization Levels
- **Public**: Health check, login, registration
- **Authenticated**: Basic user operations
- **Role-based**: Specific role requirements
- **Permission-based**: Fine-grained access control

### Audit Trail
All significant operations are logged with:
- User ID and role
- Action performed
- Resource affected
- Timestamp
- IP address
- User agent

## 🚀 API Endpoints Summary

### Authentication (`/auth`)
- POST `/login` - User authentication
- POST `/register` - User registration
- GET `/auth/me` - Current user info
- POST `/logout` - Session termination

### User Management (`/users`)
- GET `/users` - List all users (Admin/Faculty)
- GET `/users/{id}` - Get specific user
- PUT `/users/{id}` - Update user (Admin)
- DELETE `/users/{id}` - Deactivate user (Admin)

### Student Operations (`/students`, `/student`)
- GET `/students` - List students (Admin/Faculty)
- PUT `/students/{id}` - Update student (Admin/Faculty)
- POST `/students/bulk-upload` - CSV upload (Admin/Faculty)
- GET `/student/profile` - Own profile (Student)
- GET `/student/attendance` - Own attendance (Student)
- GET `/student/grades` - Own grades (Student)

### Faculty Operations (`/faculty`)
- GET `/faculty/classes` - Assigned classes
- POST `/faculty/attendance` - Mark attendance
- POST `/faculty/grades` - Record grades
- POST `/faculty/notifications` - Send notifications

### Administrative (`/admin`)
- GET `/admin/dashboard` - System statistics
- GET `/admin/audit-logs` - Activity logs
- GET `/admin/system-settings` - Configuration

## 🔧 Configuration Files

### Backend Configuration
- **alembic.ini**: Database migration settings
- **.env**: Environment variables
- **requirements.txt**: Python dependencies

### Frontend Configuration
- **package.json**: Node.js dependencies and scripts
- **vite.config.js**: Build tool configuration
- **eslint.config.js**: Code quality rules

## 📈 Scalability Features

### Horizontal Scaling
- Stateless API design
- JWT tokens (no server-side sessions)
- Database connection pooling
- Microservice-ready architecture

### Vertical Scaling
- Efficient database queries
- Pagination on list endpoints
- Lazy loading in frontend
- Optimized bundle sizes

### Extensibility
- Plugin-based permission system
- Modular component architecture
- Environment-based configuration
- Database migration system

## 🧪 Testing Strategy

### Backend Testing
- Unit tests for CRUD operations
- Integration tests for API endpoints
- Authentication flow testing
- Permission system validation

### Frontend Testing
- Component unit tests
- User interaction testing
- Route protection testing
- API integration testing

## 📦 Deployment Architecture

### Development
- Local MySQL database
- Python development server
- Vite development server
- Hot reloading enabled

### Production
- Managed database service
- Gunicorn WSGI server
- Nginx reverse proxy
- Static file serving
- SSL/TLS encryption
- Environment variable management

This structure provides a solid foundation for a scalable ERP system that can grow with your organization's needs.