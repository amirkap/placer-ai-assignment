#!/bin/bash

# Placer.ai POI Analytics Dashboard - Start Script

echo "🚀 Starting Placer.ai POI Analytics Dashboard..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ All dependencies found!"

# Start backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start FastAPI server in background
echo "🚀 Starting FastAPI backend server..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🔧 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Start React development server
echo "🚀 Starting React frontend server..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Dashboard is starting up!"
echo ""
echo "📊 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait

# Cleanup
echo ""
echo "🛑 Shutting down servers..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "✅ Servers stopped"
