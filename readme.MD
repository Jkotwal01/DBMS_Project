# Attendance Monitoring System

A full-stack web application for managing student attendance using FastAPI and React.

## 🚀 Quick Start

### Backend Setup (FastAPI + MySQL)

1. **Create and activate virtual environment:**

   ```bash
   cd backend
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database:**

   ```sql
   CREATE DATABASE attendance_db;
   ```

4. **Create `.env` file in backend directory:**

   ```env
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/attendance_db
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ```

5. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   Backend will run at http://localhost:8000

### Frontend Setup (React + Vite)

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env` file in frontend directory:**

   ```env
   VITE_API_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend will run at http://localhost:5173

## 🔑 Test Accounts

### Student Account

- Email: student@example.com
- Password: student123

### Faculty Account

- Email: faculty@example.com
- Password: faculty123

## 📚 Features

- **Authentication**

  - JWT-based authentication
  - Role-based access control
  - Protected routes

- **Student Features**

  - View attendance records
  - Check timetable
  - View notifications
  - Manage profile

- **Faculty Features**
  - Mark attendance
  - Send notifications
  - Manage classes
  - View timetables

## 🛠 Tech Stack

### Backend

- FastAPI
- SQLAlchemy ORM
- MySQL Database
- JWT Authentication
- Pydantic Models

### Frontend

- React 18
- Vite
- TailwindCSS
- React Router v6
- Axios

## 📖 API Documentation

After starting the backend server:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---------
