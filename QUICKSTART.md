# Quick Start Guide - ERP System

Get the ERP system up and running in under 10 minutes!

## 🚀 Prerequisites

Make sure you have:
- Python 3.10 or higher
- Node.js 18 or higher
- MySQL 8.0 or higher
- Git (optional)

## ⚡ Quick Setup (3 Steps)

### Step 1: Database Setup (2 minutes)

```bash
# Start MySQL and create database
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE attendance_db;
EXIT;
```

### Step 2: Backend Setup (3 minutes)

```bash
# Navigate to backend
cd backend

# Run automated setup script
python3 setup.py

# The script will:
# ✓ Check prerequisites
# ✓ Create .env file
# ✓ Install dependencies
# ✓ Guide you through database setup
# ✓ Offer to seed sample data

# OR manual setup:
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python seeds/seed_data.py

# Start backend server
uvicorn main_new:app --reload
```

Backend is now running at: **http://localhost:8000**

### Step 3: Frontend Setup (2 minutes)

```bash
# Open new terminal
cd frontend

# Install and run
npm install
npm run dev
```

Frontend is now running at: **http://localhost:5173**

## 🔑 Login & Test

### Access the Application

Open browser and go to: **http://localhost:5173**

### Test Accounts (after seeding)

**Faculty Login:**
```
Email: john.smith@university.edu
Password: faculty123
```

**Student Login:**
```
Email: alice.williams@student.edu
Password: student123
```

### Test API Directly

Visit: **http://localhost:8000/api/docs** for interactive API documentation

## ✨ What You Can Do Now

### As a Student:
1. Login with student credentials
2. View your attendance records
3. Check your timetable
4. Read notifications from faculty
5. Edit your profile

### As a Faculty:
1. Login with faculty credentials
2. View and manage students
3. Mark attendance (single or bulk)
4. Create timetables
5. Send notifications to students
6. Upload students via CSV

## 🧪 Quick API Test

### Login via API

```bash
# Get access token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice.williams@student.edu&password=student123"

# Copy the access_token from response
```

### Get Attendance

```bash
# Replace <TOKEN> with your access token
curl -X GET "http://localhost:8000/api/students/me/attendance" \
  -H "Authorization: Bearer <TOKEN>"
```

## 📊 Sample Data Included

After running seed script, you'll have:
- **3 Faculty members** (Computer Science, Mathematics, Physics)
- **5 Students** (various departments and years)
- **4 Subjects** (with faculty assignments)
- **3 Notifications** (welcome messages, announcements)

## 🎯 Next Steps

### 1. Explore the Features
- Try marking attendance as faculty
- View timetable as student
- Upload students via CSV
- Create notifications

### 2. Customize
- Add more users
- Create subjects
- Build timetables
- Configure settings in `.env`

### 3. Deploy to Production
- Follow: `DEPLOYMENT_GUIDE.md`
- Setup SSL certificates
- Configure production database
- Deploy to cloud platform

## 📚 Documentation

- **README.md** - Complete documentation
- **API_USAGE_GUIDE.md** - All API endpoints with examples
- **SCALING_GUIDE.md** - How to add roles and features
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **IMPLEMENTATION_SUMMARY.md** - What was built

## 🔧 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Try different port
uvicorn main_new:app --reload --port 8001
```

### Frontend won't start

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database connection error

```bash
# Verify MySQL is running
sudo systemctl status mysql  # Linux
brew services list           # macOS

# Test connection
mysql -u root -p attendance_db

# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

### "Module not found" errors

```bash
# Backend: Reinstall dependencies
pip install -r requirements.txt

# Frontend: Reinstall dependencies
npm install
```

## 💡 Tips

1. **Use the API docs** at `/api/docs` to test endpoints interactively
2. **Check logs** if something fails - they're very helpful
3. **Start with seed data** to see how everything works
4. **Review the code** - it's well-documented and follows best practices
5. **Try bulk operations** - upload multiple students, mark attendance for a class

## 🎓 Learning Path

1. **Day 1**: Setup and explore as student/faculty
2. **Day 2**: Try all API endpoints via Swagger UI
3. **Day 3**: Create your own students and subjects
4. **Day 4**: Understand the architecture (service layer pattern)
5. **Day 5**: Add a custom feature following SCALING_GUIDE.md

## 🚨 Important Security Note

**Default passwords are for development only!**

Before deploying to production:
1. Change all default passwords
2. Update SECRET_KEY in .env
3. Enable HTTPS
4. Review DEPLOYMENT_GUIDE.md security section

## 🎉 You're All Set!

The ERP system is now running. Explore the features, test the APIs, and customize it for your needs.

### Quick Links

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs
- **API ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

### Need Help?

- Check the comprehensive documentation
- Review API examples in API_USAGE_GUIDE.md
- Look at the implementation summary
- Read the code comments - they explain everything

---

**Happy Coding! 🚀**

For questions or issues, refer to the detailed documentation or check the inline code comments.
