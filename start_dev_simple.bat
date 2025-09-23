@echo off
REM PixelLedger Development Startup Script for Windows
REM This script starts both the frontend and backend servers for development

echo Starting PixelLedger Development Environment...
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo SUCCESS: Python, Node.js, and npm are installed

REM Install backend dependencies if needed
echo Checking backend dependencies...
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing backend dependencies (this may take a few minutes)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install backend dependencies
        pause
        exit /b 1
    )
    cd ..
) else (
    echo Backend dependencies already installed
    echo Updating dependencies...
    cd backend
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --upgrade
    if errorlevel 1 (
        echo ERROR: Failed to update backend dependencies
        pause
        exit /b 1
    )
    cd ..
)

REM Install frontend dependencies if needed
echo Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
) else (
    echo Frontend dependencies already installed
)

echo Starting backend server...
cd backend
call venv\Scripts\activate.bat
echo Testing backend startup...
python -c "from watermarking.app.core.pixel_ledger import PixelLedger; print('SUCCESS: Backend imports working')" 2>nul
if errorlevel 1 (
    echo ERROR: Backend import test failed - installing missing dependencies...
    pip install -r requirements.txt --upgrade
    python -c "from watermarking.app.core.pixel_ledger import PixelLedger; print('SUCCESS: Backend imports working')"
    if errorlevel 1 (
        echo ERROR: Backend still failing after dependency update
        pause
        exit /b 1
    )
)
start "PixelLedger Backend" cmd /k "python run_server.py"
cd ..

REM Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting frontend server...
cd frontend
start "PixelLedger Frontend" cmd /k "npm start"
cd ..

echo.
echo Development servers started!
echo ==================================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
