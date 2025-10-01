# ERP System - Scaling Guide

This guide explains how to scale the ERP system to handle more users, add new features, and maintain code quality as the system grows.

## 📋 Table of Contents

1. [Adding New Roles](#adding-new-roles)
2. [Adding New Features](#adding-new-features)
3. [Database Scaling](#database-scaling)
4. [API Performance](#api-performance)
5. [Frontend Scaling](#frontend-scaling)
6. [Security Considerations](#security-considerations)

## 🎭 Adding New Roles

The system is designed to easily accommodate new roles. Here's a step-by-step guide:

### Step 1: Define the Role in Models

**File**: `backend/models.py`

```python
class RoleEnum(str, enum.Enum):
    Student = "Student"
    Faculty = "Faculty"
    Admin = "Admin"
    Parent = "Parent"          # NEW ROLE
    Management = "Management"  # NEW ROLE
    Librarian = "Librarian"    # NEW ROLE
```

### Step 2: Create Role-Specific Model (if needed)

**File**: `backend/models.py`

```python
class Parent(Base):
    """Parent profile - linked to student(s)"""
    __tablename__ = "parents"
    
    parent_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    relation = Column(String(50))  # Father, Mother, Guardian
    occupation = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="parent")
    children = relationship("Student", secondary="parent_student", back_populates="parents")
```

### Step 3: Create Pydantic Schemas

**File**: `backend/schemas.py`

```python
class ParentBase(BaseModel):
    relation: str
    occupation: Optional[str] = None

class ParentCreate(ParentBase):
    user: UserCreate
    student_ids: List[int]  # Children

class ParentOut(BaseModel):
    parent_id: int
    relation: str
    occupation: Optional[str] = None
    user: UserOut
    
    class Config:
        from_attributes = True
```

### Step 4: Define Permissions

**File**: `backend/api/middleware/auth.py`

```python
class Permission:
    # Existing permissions...
    
    # Parent permissions
    VIEW_CHILD_ATTENDANCE = "view_child_attendance"
    VIEW_CHILD_TIMETABLE = "view_child_timetable"
    VIEW_CHILD_PERFORMANCE = "view_child_performance"
    CONTACT_TEACHERS = "contact_teachers"

# Update role-permission mapping
ROLE_PERMISSIONS = {
    "Parent": [
        Permission.VIEW_CHILD_ATTENDANCE,
        Permission.VIEW_CHILD_TIMETABLE,
        Permission.VIEW_CHILD_PERFORMANCE,
        Permission.CONTACT_TEACHERS,
    ],
    # ... other roles
}
```

### Step 5: Create Service Layer

**File**: `backend/services/parent_service.py`

```python
from sqlalchemy.orm import Session
from typing import List
import models, schemas

class ParentService:
    @staticmethod
    def create_parent(db: Session, parent_data: schemas.ParentCreate) -> models.Parent:
        # Create user first
        user = UserService.create_user(db, parent_data.user)
        
        # Create parent profile
        parent = models.Parent(
            parent_id=user.user_id,
            relation=parent_data.relation,
            occupation=parent_data.occupation
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)
        return parent
    
    @staticmethod
    def get_children_attendance(db: Session, parent_id: int):
        """Get attendance for all children"""
        parent = db.query(models.Parent).filter(models.Parent.parent_id == parent_id).first()
        if not parent:
            raise ValueError("Parent not found")
        
        # Get attendance for all children
        attendance_data = []
        for child in parent.children:
            records = db.query(models.Attendance).filter(
                models.Attendance.student_id == child.student_id
            ).all()
            attendance_data.append({
                "student": child,
                "attendance": records
            })
        
        return attendance_data
```

### Step 6: Create API Routes

**File**: `backend/api/routes/parent.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.middleware.auth import get_db, get_current_user, require_permission, Permission
import models, schemas
from services.parent_service import ParentService

router = APIRouter(prefix="/api/parents", tags=["Parents"])

@router.get("/me", response_model=schemas.ParentOut)
def get_my_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get parent profile"""
    if current_user.role.value != "Parent":
        raise HTTPException(status_code=403, detail="Parent role required")
    
    parent = db.query(models.Parent).filter(models.Parent.parent_id == current_user.user_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    return parent

@router.get("/children/attendance", dependencies=[Depends(require_permission(Permission.VIEW_CHILD_ATTENDANCE))])
def get_children_attendance(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get attendance for all children"""
    parent = db.query(models.Parent).filter(models.Parent.parent_id == current_user.user_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    
    return ParentService.get_children_attendance(db, parent.parent_id)
```

### Step 7: Update Main Application

**File**: `backend/main_new.py`

```python
from api.routes import auth, student, faculty, subjects, parent  # Add parent

# Include router
app.include_router(parent.router)
```

### Step 8: Create Database Migration

```bash
cd backend
alembic revision -m "Add parent role and table"
```

Edit the migration file to add the parent table and relationships.

### Step 9: Create Frontend Components

**File**: `frontend/src/pages/ParentDashboard.jsx`

```jsx
import React, { useEffect, useState } from 'react';
import api from '../api';

export default function ParentDashboard() {
    const [children, setChildren] = useState([]);
    
    useEffect(() => {
        fetchChildrenData();
    }, []);
    
    const fetchChildrenData = async () => {
        const response = await api.get('/api/parents/children/attendance');
        setChildren(response.data);
    };
    
    return (
        <div className="container mx-auto p-6">
            <h1 className="text-3xl font-bold mb-6">Parent Dashboard</h1>
            {/* Render children data */}
        </div>
    );
}
```

### Step 10: Add Routes in Frontend

**File**: `frontend/src/App.jsx`

```jsx
// Add parent routes
<Route
    path="/parent/*"
    element={
        <ProtectedRoute allowedRoles={["parent"]}>
            <div>
                <Navbar />
                <Routes>
                    <Route path="dashboard" element={<ParentDashboard />} />
                    <Route path="children" element={<ChildrenList />} />
                    <Route path="profile" element={<Profile />} />
                </Routes>
            </div>
        </ProtectedRoute>
    }
/>
```

## 🚀 Adding New Features

### Example: Adding Grade Management

1. **Create Model** (`models.py`):
```python
class Grade(Base):
    __tablename__ = "grades"
    grade_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    exam_type = Column(String(50))  # Midterm, Final, Quiz
    marks = Column(Integer)
    max_marks = Column(Integer)
    date = Column(Date)
    graded_by = Column(Integer, ForeignKey("faculty.faculty_id"))
```

2. **Create Schemas** (`schemas.py`):
```python
class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    exam_type: str
    marks: int
    max_marks: int
    date: date

class GradeOut(BaseModel):
    grade_id: int
    student_id: int
    subject_id: int
    exam_type: str
    marks: int
    max_marks: int
    date: date
    percentage: float
```

3. **Create Service** (`services/grade_service.py`)

4. **Create Routes** (`api/routes/grades.py`)

5. **Add to Main App**

6. **Create Frontend Components**

## 💾 Database Scaling

### 1. Indexing Strategy

Add indexes for frequently queried columns:

```python
# In models.py
class Attendance(Base):
    # ... existing code
    
    # Add composite index
    __table_args__ = (
        Index('idx_student_date', 'student_id', 'date'),
        Index('idx_subject_date', 'subject_id', 'date'),
    )
```

### 2. Database Sharding (for very large scale)

Separate databases by:
- Department
- Academic year
- Geographic location

### 3. Read Replicas

For read-heavy operations:
- Use read replicas for GET requests
- Master database for write operations

```python
# database.py
read_engine = create_engine(READ_REPLICA_URL)
write_engine = create_engine(MASTER_DB_URL)
```

### 4. Caching Strategy

Use Redis for frequently accessed data:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## ⚡ API Performance

### 1. Pagination

Always paginate large result sets:

```python
@router.get("/students")
def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    students = db.query(Student).offset(skip).limit(limit).all()
    total = db.query(Student).count()
    return {
        "items": students,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### 2. Lazy Loading vs Eager Loading

Use joinedload for frequently accessed relationships:

```python
from sqlalchemy.orm import joinedload

students = db.query(Student).options(
    joinedload(Student.user),
    joinedload(Student.attendance)
).all()
```

### 3. Async Operations (for I/O bound tasks)

```python
from fastapi import BackgroundTasks

def send_notification_email(email: str, message: str):
    # Send email logic
    pass

@router.post("/notifications")
async def create_notification(
    data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    notification = create_notification(db, data)
    
    # Send emails in background
    background_tasks.add_task(send_notification_email, "user@example.com", notification.title)
    
    return notification
```

### 4. Response Compression

Enable gzip compression:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## 🎨 Frontend Scaling

### 1. Code Splitting

Split routes for lazy loading:

```jsx
import React, { lazy, Suspense } from 'react';

const StudentDashboard = lazy(() => import('./pages/StudentDashboard'));
const FacultyDashboard = lazy(() => import('./pages/FacultyDashboard'));

function App() {
    return (
        <Suspense fallback={<Loading />}>
            <Routes>
                <Route path="/student/dashboard" element={<StudentDashboard />} />
                <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
            </Routes>
        </Suspense>
    );
}
```

### 2. State Management

For larger apps, use Redux or Zustand:

```jsx
// store/useAuthStore.js
import create from 'zustand';

const useAuthStore = create((set) => ({
    user: null,
    token: null,
    login: (user, token) => set({ user, token }),
    logout: () => set({ user: null, token: null }),
}));
```

### 3. API Service Layer

Centralize API calls:

```javascript
// services/api.service.js
class ApiService {
    async getStudents(params) {
        return api.get('/api/students', { params });
    }
    
    async createStudent(data) {
        return api.post('/api/students', data);
    }
    
    // ... more methods
}

export default new ApiService();
```

### 4. Component Library

Create reusable components:

```jsx
// components/ui/DataTable.jsx
export function DataTable({ columns, data, onRowClick }) {
    // Reusable table component
}

// components/ui/Modal.jsx
export function Modal({ isOpen, onClose, children }) {
    // Reusable modal component
}
```

## 🔒 Security Considerations

### 1. Rate Limiting

Prevent abuse with rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, ...):
    # Login logic
```

### 2. Input Sanitization

Always validate and sanitize input:

```python
from pydantic import validator

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v) > 100:
            raise ValueError('Name too long')
        return v.strip()
```

### 3. Audit Logging

Track all important actions:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(String(50))  # CREATE, UPDATE, DELETE
    entity_type = Column(String(50))  # Student, Faculty, etc.
    entity_id = Column(Integer)
    changes = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(TIMESTAMP, server_default=func.now())

def log_action(db, user_id, action, entity_type, entity_id, changes, ip):
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip
    )
    db.add(log)
    db.commit()
```

### 4. Environment-based Configuration

Never hardcode sensitive data:

```python
# config/settings.py
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Different configs for different environments
class DevelopmentSettings(Settings):
    DEBUG: bool = True

class ProductionSettings(Settings):
    DEBUG: bool = False
    # Additional production settings
```

## 📊 Monitoring and Analytics

### 1. Application Metrics

Track performance:

```python
import time
from functools import wraps

def track_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        # Log to monitoring service
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper
```

### 2. Error Tracking

Use Sentry or similar:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

## 🔄 Continuous Integration/Deployment

### 1. Automated Testing

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
```

### 2. Database Migration Automation

Always run migrations in CI/CD:

```yaml
- name: Run migrations
  run: alembic upgrade head
```

## 📈 Performance Benchmarks

Target performance metrics:
- API response time: < 200ms (p95)
- Page load time: < 2s
- Database query time: < 100ms (p95)
- Concurrent users: 1000+
- Requests per second: 100+

## 🎯 Best Practices Checklist

- [ ] Use database transactions for multi-step operations
- [ ] Implement proper error handling and logging
- [ ] Add request/response validation
- [ ] Use connection pooling for database
- [ ] Implement caching for frequently accessed data
- [ ] Add rate limiting on sensitive endpoints
- [ ] Use HTTPS in production
- [ ] Regular security audits
- [ ] Document all API endpoints
- [ ] Write unit and integration tests
- [ ] Monitor application performance
- [ ] Regular database backups
- [ ] Keep dependencies updated

---

This guide will help you scale the ERP system effectively while maintaining code quality and performance.
