#!/bin/bash

# Enhanced ERP System Setup Script
# This script sets up the complete ERP system with all dependencies

set -e  # Exit on any error

echo "🚀 Enhanced ERP System Setup"
echo "=============================="

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

# Check if running as root for MySQL setup
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_warning "This script requires sudo access for MySQL setup"
        print_status "Please enter your password when prompted"
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install Python 3, pip, and development tools
    sudo apt install -y python3 python3-pip python3-venv python3-dev
    
    # Install Node.js and npm
    if ! command -v node &> /dev/null; then
        print_status "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
    
    # Install MySQL if not present
    if ! command -v mysql &> /dev/null; then
        print_status "Installing MySQL Server..."
        sudo apt install -y mysql-server
        
        # Start MySQL service
        sudo systemctl start mysql || sudo mysqld_safe --user=mysql --datadir=/var/lib/mysql &
        sleep 5
    fi
    
    print_success "System dependencies installed"
}

# Setup MySQL database
setup_database() {
    print_status "Setting up MySQL database..."
    
    # Create database user and database
    sudo mysql -e "CREATE USER IF NOT EXISTS 'erp_user'@'localhost' IDENTIFIED BY 'erp_password';" 2>/dev/null || true
    sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'erp_user'@'localhost';" 2>/dev/null || true
    sudo mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true
    sudo mysql -e "CREATE DATABASE IF NOT EXISTS attendance_db;" 2>/dev/null || true
    
    print_success "MySQL database configured"
}

# Setup Python backend
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd backend
    
    # Install Python dependencies
    pip3 install -r requirements.txt --user
    
    # Run database migrations
    print_status "Running database migrations..."
    python3 -m alembic upgrade head
    
    # Create initial users
    print_status "Creating initial users..."
    python3 create_users.py
    
    # Seed additional data
    print_status "Seeding database with sample data..."
    python3 seed_data.py || print_warning "Some seed data may have failed - this is normal"
    
    cd ..
    print_success "Backend setup completed"
}

# Setup React frontend
setup_frontend() {
    print_status "Setting up React frontend..."
    
    cd frontend
    
    # Install Node.js dependencies
    npm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > backend/.env << EOF
DATABASE_URL=mysql+pymysql://erp_user:erp_password@localhost:3306/attendance_db
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
EOF
    
    print_success "Environment file created"
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend startup script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "Starting Enhanced ERP Backend..."
cd backend
python3 main_enhanced.py
EOF
    
    # Frontend startup script
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "Starting Enhanced ERP Frontend..."
cd frontend
npm run dev
EOF
    
    # Make scripts executable
    chmod +x start_backend.sh start_frontend.sh
    
    print_success "Startup scripts created"
}

# Display final instructions
show_final_instructions() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "=================="
    echo ""
    echo "📋 Default Login Credentials:"
    echo "   Admin:   admin@erp.edu / admin123"
    echo "   Faculty: john.smith@erp.edu / faculty123"
    echo "   Student: alice.brown@student.erp.edu / student123"
    echo ""
    echo "🚀 To start the system:"
    echo "   Backend:  ./start_backend.sh"
    echo "   Frontend: ./start_frontend.sh"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📁 Sample Files:"
    echo "   CSV Upload: backend/sample_students.csv"
    echo ""
    echo "📖 Documentation:"
    echo "   Full docs: README.md"
    echo ""
    print_success "Enhanced ERP System is ready to use!"
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    check_sudo
    install_system_deps
    setup_database
    create_env_file
    setup_backend
    setup_frontend
    create_startup_scripts
    show_final_instructions
}

# Run main function
main "$@"