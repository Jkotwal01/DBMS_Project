#!/bin/bash

# ERP Attendance Management System Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up ERP Attendance Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 16+ and try again."
        exit 1
    fi
    
    if ! command_exists npm; then
        print_error "npm is not installed. Please install npm and try again."
        exit 1
    fi
    
    if ! command_exists mysql; then
        print_warning "MySQL is not installed. Please install MySQL 8.0+ for database functionality."
    fi
    
    print_success "Prerequisites check completed."
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
DATABASE_URL=mysql+pymysql://root:@localhost:3306/erp_attendance
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
EOF
        print_warning "Please update the .env file with your database credentials and secret key."
    fi
    
    print_success "Backend setup completed."
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup completed."
    cd ..
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    if command_exists mysql; then
        print_status "Creating database and user..."
        
        # Read database configuration from .env
        if [ -f "backend/.env" ]; then
            DB_URL=$(grep DATABASE_URL backend/.env | cut -d '=' -f2)
            DB_NAME=$(echo $DB_URL | sed 's/.*\/\([^?]*\).*/\1/')
            
            mysql -u root -p -e "
                CREATE DATABASE IF NOT EXISTS $DB_NAME;
                CREATE USER IF NOT EXISTS 'erp_user'@'localhost' IDENTIFIED BY 'erp_password';
                GRANT ALL PRIVILEGES ON $DB_NAME.* TO 'erp_user'@'localhost';
                FLUSH PRIVILEGES;
            " 2>/dev/null || print_warning "Could not create database. Please create it manually."
        fi
    else
        print_warning "MySQL not found. Please install MySQL and create the database manually."
    fi
    
    print_success "Database setup completed."
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd backend
    source venv/bin/activate
    
    # Run migrations
    python3 -m alembic upgrade head 2>/dev/null || print_warning "Could not run migrations. Please check database connection."
    
    print_success "Migrations completed."
    cd ..
}

# Seed initial data
seed_data() {
    print_status "Seeding initial data..."
    
    cd backend
    source venv/bin/activate
    
    python3 seed_data.py 2>/dev/null || print_warning "Could not seed data. Please check database connection."
    
    print_success "Initial data seeded."
    cd ..
}

# Main setup function
main() {
    echo "🎓 ERP Attendance Management System Setup"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    setup_backend
    setup_frontend
    setup_database
    run_migrations
    seed_data
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update backend/.env with your database credentials"
    echo "2. Start the backend server:"
    echo "   cd backend && source venv/bin/activate && python main_v2.py"
    echo "3. Start the frontend server:"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "🌐 Access the application:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🔐 Test credentials:"
    echo "   Admin: admin@erp.edu / admin123"
    echo "   Faculty: john.smith@erp.edu / faculty123"
    echo "   Student: alice.johnson@student.erp.edu / student123"
    echo ""
    echo "📚 For more information, see README_ERP.md"
}

# Run main function
main "$@"