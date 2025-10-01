# ERP Attendance Management System - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:
```json
{
  "data": {}, // Response data
  "message": "Success", // Optional message
  "status": "success" // success or error
}
```

Error responses:
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Authentication Endpoints

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_role": "Student"
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "Student",
  "department": "CS"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```

## User Management

### Get All Users (Admin only)
```http
GET /users?skip=0&limit=100
Authorization: Bearer <admin-token>
```

### Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer <token>
```

### Update User
```http
PUT /users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

## Student Management

### Get All Students
```http
GET /students?skip=0&limit=100&dept_id=1
Authorization: Bearer <faculty-token>
```

### Get Student by ID
```http
GET /students/{student_id}
Authorization: Bearer <token>
```

### Create Student Profile
```http
POST /students/{student_id}/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "roll_no": "CS2024001",
  "class_name": "B.Tech CSE",
  "year": 2024,
  "section": "A",
  "batch": "2024",
  "dept_id": 1
}
```

### Update Student Profile
```http
PUT /students/{student_id}/profile
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "roll_no": "CS2024001",
  "class_name": "B.Tech CSE",
  "year": 2024,
  "section": "A"
}
```

## Faculty Management

### Get All Faculty
```http
GET /faculty?skip=0&limit=100&dept_id=1
Authorization: Bearer <token>
```

### Get Faculty by ID
```http
GET /faculty/{faculty_id}
Authorization: Bearer <token>
```

### Create Faculty Profile
```http
POST /faculty/{faculty_id}/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "employee_id": "FAC001",
  "designation": "Professor",
  "dept_id": 1,
  "qualification": "PhD in Computer Science",
  "specialization": "Machine Learning",
  "experience_years": 15
}
```

## Attendance Management

### Get Student Attendance
```http
GET /attendance/student/{student_id}?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <token>
```

### Get Attendance Summary
```http
GET /attendance/summary/{student_id}?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_sessions": 50,
  "present_count": 45,
  "absent_count": 5,
  "attendance_percentage": 90.0
}
```

### Mark Attendance
```http
POST /attendance/mark
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "session_id": 1,
  "student_id": 1,
  "status": "Present",
  "remarks": "On time"
}
```

### Bulk Mark Attendance
```http
POST /attendance/bulk-mark
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "session_id": 1,
  "attendance_records": [
    {
      "student_id": 1,
      "status": "Present",
      "remarks": "On time"
    },
    {
      "student_id": 2,
      "status": "Absent",
      "remarks": "Sick leave"
    }
  ]
}
```

## Notification System

### Get Notifications
```http
GET /notifications?skip=0&limit=50
Authorization: Bearer <token>
```

### Create Notification
```http
POST /notifications
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "title": "Important Announcement",
  "message": "Class will be cancelled tomorrow",
  "notification_type": "General",
  "target_role": "Student",
  "is_urgent": true
}
```

## Timetable Management

### Get Student Timetable
```http
GET /timetable/student/{student_id}?semester_id=1
Authorization: Bearer <token>
```

### Get Faculty Timetable
```http
GET /timetable/faculty/{faculty_id}?semester_id=1
Authorization: Bearer <token>
```

## Dashboard Endpoints

### Student Dashboard
```http
GET /dashboard/student
Authorization: Bearer <student-token>
```

**Response:**
```json
{
  "user": {
    "user_id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "Student"
  },
  "student": {
    "student_id": 1,
    "roll_no": "CS2024001",
    "class_name": "B.Tech CSE",
    "year": 2024,
    "section": "A"
  },
  "attendance_summary": {
    "total_sessions": 50,
    "present_count": 45,
    "absent_count": 5,
    "attendance_percentage": 90.0
  },
  "recent_notifications": [...],
  "upcoming_classes": [...]
}
```

### Faculty Dashboard
```http
GET /dashboard/faculty
Authorization: Bearer <faculty-token>
```

## Bulk Upload

### Upload Students
```http
POST /upload/students
Authorization: Bearer <admin-token>
Content-Type: application/json

[
  {
    "name": "John Doe",
    "email": "john@example.com",
    "roll_no": "CS2024002",
    "class_name": "B.Tech CSE",
    "year": 2024,
    "section": "A",
    "batch": "2024",
    "department": "CS"
  }
]
```

### Upload Faculty
```http
POST /upload/faculty
Authorization: Bearer <admin-token>
Content-Type: application/json

[
  {
    "name": "Dr. Jane Smith",
    "email": "jane@example.com",
    "employee_id": "FAC002",
    "designation": "Assistant Professor",
    "department": "IT"
  }
]
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per hour per user

## Data Models

### User
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "Student",
  "department": "CS",
  "phone": "+1234567890",
  "status": "Active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Student
```json
{
  "student_id": 1,
  "roll_no": "CS2024001",
  "class_name": "B.Tech CSE",
  "year": 2024,
  "section": "A",
  "batch": "2024",
  "dept_id": 1,
  "gpa": 8.5,
  "total_credits": 120
}
```

### Faculty
```json
{
  "faculty_id": 1,
  "employee_id": "FAC001",
  "designation": "Professor",
  "dept_id": 1,
  "qualification": "PhD in Computer Science",
  "specialization": "Machine Learning",
  "experience_years": 15
}
```

### Attendance
```json
{
  "attendance_id": 1,
  "session_id": 1,
  "student_id": 1,
  "status": "Present",
  "remarks": "On time",
  "marked_at": "2024-01-01T09:00:00Z",
  "marked_by": 2
}
```

### Notification
```json
{
  "notification_id": 1,
  "title": "Important Announcement",
  "message": "Class cancelled tomorrow",
  "notification_type": "General",
  "sender_id": 2,
  "target_role": "Student",
  "is_urgent": true,
  "created_at": "2024-01-01T10:00:00Z"
}
```

## WebSocket Events (Future Enhancement)

Real-time updates will be available via WebSocket connections:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function() {
    // Authenticate
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your-jwt-token'
    }));
};
```

### Events
- `attendance_updated` - When attendance is marked
- `notification_created` - When new notification is created
- `timetable_changed` - When timetable is updated

## SDK Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Get student dashboard
const dashboard = await api.get('/dashboard/student');

// Mark attendance
await api.post('/attendance/mark', {
  session_id: 1,
  student_id: 1,
  status: 'Present'
});
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {token}'}

# Get faculty dashboard
response = requests.get('http://localhost:8000/dashboard/faculty', headers=headers)
dashboard = response.json()

# Create notification
data = {
    'title': 'Test Notification',
    'message': 'This is a test',
    'target_role': 'Student'
}
response = requests.post('http://localhost:8000/notifications', json=data, headers=headers)
```

## Testing

### Using curl
```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@erp.edu&password=admin123"

# Get dashboard
curl -X GET "http://localhost:8000/dashboard/student" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Postman
1. Import the API collection
2. Set the base URL to `http://localhost:8000`
3. Use the login endpoint to get a token
4. Set the token in the Authorization header for other requests

---

For interactive API documentation, visit `http://localhost:8000/docs` when the server is running.