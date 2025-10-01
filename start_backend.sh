#!/bin/bash
echo "🚀 Starting Enhanced ERP Backend..."
echo "=================================="

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  Starting MySQL..."
    sudo mysqld_safe --user=mysql --datadir=/var/lib/mysql &
    sleep 3
fi

# Navigate to backend directory
cd backend

# Start the FastAPI server
echo "🌐 Backend will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

python3 main_enhanced.py