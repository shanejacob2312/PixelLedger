# PixelLedger PowerShell Start Script
# This script starts both the frontend and backend servers for development

Write-Host "🚀 Starting PixelLedger Development Environment..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 16+ first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "npm not found"
    }
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed. Please install npm first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if backend virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "Installing backend dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
} else {
    Write-Host "📦 Backend dependencies already installed" -ForegroundColor Green
}

# Check if frontend node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Set-Location ..
} else {
    Write-Host "📦 Frontend dependencies already installed" -ForegroundColor Green
}

# Start backend server
Write-Host "🔧 Starting backend server..." -ForegroundColor Blue
Set-Location backend
& "venv\Scripts\Activate.ps1"
Start-Process -FilePath "cmd" -ArgumentList "/c", "venv\Scripts\activate.bat && python run_server.py" -WindowStyle Normal
Set-Location ..

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "🎨 Starting frontend server..." -ForegroundColor Magenta
Set-Location frontend
Start-Process -FilePath "cmd" -ArgumentList "/c", "npm start" -WindowStyle Normal
Set-Location ..

Write-Host ""
Write-Host "🎉 Development servers started!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Blue
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "🔍 Health Check: http://localhost:8000/api/health" -ForegroundColor Blue
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Yellow
Write-Host "Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
