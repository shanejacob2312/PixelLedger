@echo off
REM PixelLedger Development Startup Script for Windows
REM This script starts both the frontend and backend servers for development

echo 🚀 Starting PixelLedger Development Environment...
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ Python, Node.js, and npm are installed

REM Install backend dependencies if needed
echo 📦 Checking backend dependencies...
if not exist "backend\venv" (
    echo    Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
) else (
    echo    Backend dependencies already installed
)

REM Install frontend dependencies if needed
echo 📦 Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo    Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
) else (
    echo    Frontend dependencies already installed
)

echo 🔧 Starting backend server...
cd backend
call venv\Scripts\activate.bat
start "PixelLedger Backend" cmd /k "python run_server.py"
cd ..

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo 🎨 Starting frontend server...
cd frontend
start "PixelLedger Frontend" cmd /k "npm start"
cd ..

echo.
echo 🎉 Development servers started!
echo ==================================================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/api/health
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
