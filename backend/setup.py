#!/usr/bin/env python3
"""
Setup script for ERP System backend
Automates initial setup process
"""
import os
import sys
import subprocess
from pathlib import Path

def print_step(step, message):
    """Print colored step message"""
    print(f"\n{'='*60}")
    print(f"Step {step}: {message}")
    print(f"{'='*60}\n")

def run_command(cmd, description):
    """Run shell command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed"""
    print_step(1, "Checking Prerequisites")
    
    # Check Python
    print("✓ Python:", sys.version)
    
    # Check pip
    if not run_command("pip --version", "Checking pip"):
        print("❌ pip not found. Please install pip.")
        return False
    
    # Check MySQL
    if not run_command("mysql --version", "Checking MySQL"):
        print("⚠️  MySQL not found. Please ensure MySQL is installed and running.")
        return False
    
    return True

def create_env_file():
    """Create .env file from example"""
    print_step(2, "Creating Environment Configuration")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    # Copy example to .env
    with open(env_example, 'r') as f:
        env_content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env file from .env.example")
    print("⚠️  Please update DATABASE_URL and SECRET_KEY in .env file")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(3, "Installing Dependencies")
    
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    print("✓ All dependencies installed successfully")
    return True

def create_database():
    """Create MySQL database"""
    print_step(4, "Database Setup")
    
    print("Please ensure you have:")
    print("  1. MySQL server running")
    print("  2. Created database: CREATE DATABASE attendance_db;")
    print("  3. Updated DATABASE_URL in .env file")
    
    response = input("\nHave you completed the database setup? (y/n): ")
    if response.lower() != 'y':
        print("⚠️  Please complete database setup manually and run this script again")
        return False
    
    return True

def run_migrations():
    """Run database migrations"""
    print_step(5, "Running Database Migrations")
    
    print("Note: Tables will be auto-created when you start the server")
    print("For production, you should use Alembic migrations:")
    print("  alembic upgrade head")
    
    return True

def seed_database():
    """Seed database with initial data"""
    print_step(6, "Seeding Database")
    
    response = input("Do you want to seed the database with sample data? (y/n): ")
    if response.lower() != 'y':
        print("⚠️  Skipping database seeding")
        return True
    
    if not run_command("python seeds/seed_data.py", "Seeding database"):
        print("❌ Failed to seed database")
        return False
    
    print("✓ Database seeded successfully")
    return True

def print_completion():
    """Print completion message with next steps"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. Review and update .env file with your configuration")
    print("2. Ensure MySQL database 'attendance_db' is created")
    print("3. Start the backend server:")
    print("   uvicorn main_new:app --reload")
    print("\n4. Access API documentation:")
    print("   http://localhost:8000/api/docs")
    print("\n5. Setup frontend:")
    print("   cd ../frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n🔑 Default Login Credentials (after seeding):")
    print("\n   Faculty:")
    print("   📧 john.smith@university.edu")
    print("   🔒 faculty123")
    print("\n   Student:")
    print("   📧 alice.williams@student.edu")
    print("   🔒 student123")
    print("\n" + "="*60 + "\n")

def main():
    """Main setup function"""
    print("\n🚀 ERP System Backend Setup")
    print("This script will help you set up the backend environment\n")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    steps = [
        check_prerequisites,
        create_env_file,
        install_dependencies,
        create_database,
        run_migrations,
        seed_database
    ]
    
    for step in steps:
        if not step():
            print("\n❌ Setup failed. Please resolve the errors and try again.")
            sys.exit(1)
    
    print_completion()

if __name__ == "__main__":
    main()
