# API Usage Guide

Complete guide for using the ERP System API with examples.

## 🔑 Authentication

All API requests (except login/register) require authentication via JWT token.

### Register a New User

```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "role": "Student",
  "department": "Computer Science",
  "phone": "1234567890",
  "address": "123 Main St"
}
```

**Response:**
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "Student",
  "department": "Computer Science",
  "phone": "1234567890",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john.doe@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Verify Token

```http
GET /api/auth/me
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "Student",
  "department": "Computer Science",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

## 👨‍🎓 Student APIs

### Get My Profile

```http
GET /api/students/me
Authorization: Bearer <student-token>
```

### Update My Profile

```http
PUT /api/students/me/profile
Authorization: Bearer <student-token>
Content-Type: application/json

{
  "roll_no": "CS2024001",
  "class_name": "Computer Science",
  "year": 2,
  "section": "A",
  "division": "1",
  "batch": "2024"
}
```

### Get My Attendance

```http
GET /api/students/me/attendance
Authorization: Bearer <student-token>

# With filters
GET /api/students/me/attendance?subject_id=1&start_date=2024-01-01&end_date=2024-03-31
```

**Response:**
```json
[
  {
    "attendance_id": 1,
    "student_id": 1,
    "subject_id": 1,
    "date": "2024-03-15",
    "status": "Present",
    "marked_by": 10,
    "remarks": null,
    "created_at": "2024-03-15T10:00:00",
    "updated_at": "2024-03-15T10:00:00",
    "subject_name": "Data Structures",
    "marked_by_name": "Dr. John Smith"
  }
]
```

### Get Attendance Statistics

```http
GET /api/students/me/attendance/stats
Authorization: Bearer <student-token>

# For specific subject
GET /api/students/me/attendance/stats?subject_id=1
```

**Response:**
```json
{
  "total_classes": 30,
  "present": 27,
  "absent": 2,
  "late": 1,
  "excused": 0,
  "attendance_percentage": 90.0
}
```

### Get My Timetable

```http
GET /api/students/me/timetable
Authorization: Bearer <student-token>

# For specific day
GET /api/students/me/timetable?day=Monday
```

**Response:**
```json
[
  {
    "timetable_id": 1,
    "subject_id": 1,
    "student_id": 1,
    "day": "Monday",
    "time_slot": "09:00-10:00",
    "room_number": "Room 101",
    "semester": 3,
    "academic_year": "2024-2025",
    "subject_name": "Data Structures",
    "subject_code": "CS101"
  }
]
```

### Get My Notifications

```http
GET /api/students/me/notifications
Authorization: Bearer <student-token>

# With pagination
GET /api/students/me/notifications?skip=0&limit=20
```

## 👨‍🏫 Faculty APIs

### Get My Profile

```http
GET /api/faculty/me
Authorization: Bearer <faculty-token>
```

### Update My Profile

```http
PUT /api/faculty/me/profile
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "employee_id": "FAC001",
  "designation": "Professor",
  "dept": "Computer Science",
  "specialization": "Artificial Intelligence"
}
```

### Get My Subjects

```http
GET /api/faculty/me/subjects
Authorization: Bearer <faculty-token>
```

### Mark Attendance (Single Student)

```http
POST /api/faculty/attendance
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "student_id": 1,
  "subject_id": 1,
  "date": "2024-03-15",
  "status": "Present",
  "remarks": "On time"
}
```

**Valid status values:** `Present`, `Absent`, `Late`, `Excused`

### Bulk Mark Attendance

```http
POST /api/faculty/attendance/bulk
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "subject_id": 1,
  "date": "2024-03-15",
  "attendance_list": [
    {"student_id": 1, "status": "Present"},
    {"student_id": 2, "status": "Absent", "remarks": "Sick"},
    {"student_id": 3, "status": "Late"},
    {"student_id": 4, "status": "Present"}
  ]
}
```

**Response:**
```json
{
  "success_count": 4,
  "error_count": 0,
  "errors": [],
  "message": "Successfully marked attendance for 4 students. 0 errors."
}
```

### Get Subject Attendance

```http
GET /api/faculty/attendance/subject/1
Authorization: Bearer <faculty-token>

# For specific date
GET /api/faculty/attendance/subject/1?date_val=2024-03-15
```

### Delete Attendance Record

```http
DELETE /api/faculty/attendance/123
Authorization: Bearer <faculty-token>
```

### Create Timetable Entry

```http
POST /api/faculty/timetable
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "subject_id": 1,
  "student_id": 1,
  "day": "Monday",
  "time_slot": "09:00-10:00",
  "room_number": "Room 101",
  "semester": 3,
  "academic_year": "2024-2025"
}
```

### Bulk Create Timetable

```http
POST /api/faculty/timetable/bulk
Authorization: Bearer <faculty-token>
Content-Type: application/json

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

### Delete Timetable Entry

```http
DELETE /api/faculty/timetable/123
Authorization: Bearer <faculty-token>
```

### Create Notification

```http
POST /api/faculty/notifications
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "title": "Midterm Exam Announcement",
  "description": "Midterm exams will be held next week. Please prepare accordingly.",
  "visible_to": "Student",
  "priority": "high"
}
```

**visible_to options:** `Student`, `Faculty`, `All`  
**priority options:** `low`, `normal`, `high`, `urgent`

### Get My Notifications

```http
GET /api/faculty/notifications
Authorization: Bearer <faculty-token>
```

### Delete Notification

```http
DELETE /api/faculty/notifications/123
Authorization: Bearer <faculty-token>
```

## 📊 Student Management (Faculty/Admin)

### Create Student

```http
POST /api/students/
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "user": {
    "name": "Jane Smith",
    "email": "jane.smith@student.edu",
    "password": "student123",
    "role": "Student",
    "department": "Computer Science",
    "phone": "9876543210"
  },
  "roll_no": "CS2024010",
  "class_name": "Computer Science",
  "year": 2,
  "section": "B",
  "division": "1",
  "batch": "2024"
}
```

### Get All Students

```http
GET /api/students/
Authorization: Bearer <faculty-token>

# With filters and pagination
GET /api/students/?skip=0&limit=100&class_name=Computer%20Science&year=2&section=A
```

### Get Student by ID

```http
GET /api/students/123
Authorization: Bearer <faculty-token>
```

### Update Student

```http
PUT /api/students/123
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "roll_no": "CS2024010",
  "class_name": "Computer Science",
  "year": 3,
  "section": "A"
}
```

### Delete Student

```http
DELETE /api/students/123
Authorization: Bearer <faculty-token>
```

### Bulk Upload Students (CSV)

```http
POST /api/faculty/students/bulk-upload
Authorization: Bearer <faculty-token>
Content-Type: multipart/form-data

file: students.csv
```

**CSV Format:**
```csv
name,email,password,roll_no,class_name,year,section,division,batch,department,phone,address
John Doe,john@student.edu,student123,CS2024001,Computer Science,2,A,1,2024,CS,1234567890,123 Main St
Jane Smith,jane@student.edu,student123,CS2024002,Computer Science,2,A,1,2024,CS,9876543210,456 Oak Ave
```

**Response:**
```json
{
  "success_count": 2,
  "error_count": 0,
  "errors": [],
  "message": "Successfully created 2 students. 0 errors."
}
```

### Get CSV Template

```http
GET /api/faculty/students/csv-template
Authorization: Bearer <faculty-token>
```

## 📚 Subject Management

### Create Subject

```http
POST /api/subjects/
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "subject_code": "CS101",
  "subject_name": "Data Structures and Algorithms",
  "faculty_id": 10,
  "semester": 3,
  "credits": 4,
  "department": "Computer Science"
}
```

### Get All Subjects

```http
GET /api/subjects/
Authorization: Bearer <any-token>

# With filters
GET /api/subjects/?department=Computer%20Science&semester=3
```

### Get Subject by ID

```http
GET /api/subjects/1
Authorization: Bearer <any-token>
```

### Update Subject

```http
PUT /api/subjects/1
Authorization: Bearer <faculty-token>
Content-Type: application/json

{
  "subject_name": "Advanced Data Structures",
  "credits": 5
}
```

### Delete Subject

```http
DELETE /api/subjects/1
Authorization: Bearer <faculty-token>
```

## 🔧 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: Faculty"
}
```

### 404 Not Found
```json
{
  "detail": "Student not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## 🧪 Testing with cURL

### Login Example

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice.williams@student.edu&password=student123"
```

### Get Attendance with Token

```bash
TOKEN="your-jwt-token-here"

curl -X GET "http://localhost:8000/api/students/me/attendance" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Student

```bash
curl -X POST "http://localhost:8000/api/students/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "name": "Test Student",
      "email": "test@student.edu",
      "password": "student123",
      "role": "Student"
    },
    "roll_no": "CS2024999"
  }'
```

## 🐍 Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={
        "username": "alice.williams@student.edu",
        "password": "student123"
    }
)
token = response.json()["access_token"]

# Get attendance
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    f"{BASE_URL}/api/students/me/attendance",
    headers=headers
)
attendance = response.json()
print(attendance)

# Mark attendance (faculty)
response = requests.post(
    f"{BASE_URL}/api/faculty/attendance",
    headers=headers,
    json={
        "student_id": 1,
        "subject_id": 1,
        "date": "2024-03-15",
        "status": "Present"
    }
)
```

## 📱 Testing with JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';

// Login
async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    });
    
    const data = await response.json();
    return data.access_token;
}

// Get attendance
async function getAttendance(token) {
    const response = await fetch(`${BASE_URL}/api/students/me/attendance`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return await response.json();
}

// Usage
const token = await login('alice.williams@student.edu', 'student123');
const attendance = await getAttendance(token);
console.log(attendance);
```

## 🔐 Rate Limiting

Some endpoints may have rate limiting:
- Login: 5 attempts per minute
- Bulk operations: 10 requests per minute

## 📊 Pagination

For endpoints returning lists, use `skip` and `limit` parameters:

```http
GET /api/students/?skip=0&limit=50
```

Default: `skip=0`, `limit=100`  
Maximum: `limit=1000`

## 🎯 Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in localStorage for sensitive apps)
3. **Refresh tokens before expiry**
4. **Handle errors gracefully**
5. **Use pagination for large datasets**
6. **Validate input on client side**
7. **Use bulk endpoints for multiple operations**
8. **Log out when done** (remove token)

---

For more information, visit the interactive API docs at `/api/docs` after starting the server.
