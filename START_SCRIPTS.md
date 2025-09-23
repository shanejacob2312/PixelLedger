# PixelLedger Start Scripts

This document explains all the available start scripts for running the PixelLedger development environment.

## Quick Start

The easiest way to start both frontend and backend:

```bash
npm start
```

## Available Start Scripts

### 1. NPM Scripts (Recommended)

```bash
# Start both frontend and backend
npm start

# Start only frontend
npm run start:frontend

# Start only backend  
npm run start:backend

# Install all dependencies
npm run install:all

# Build frontend for production
npm run build
```

### 2. Platform-Specific Scripts

#### Windows (Batch Files)
```cmd
# Enhanced version with emojis and better UI
start_dev.bat

# Simple version
start_dev_simple.bat
```

#### Windows (PowerShell)
```powershell
# PowerShell version with better error handling
.\start.ps1
```

#### Unix/Linux/macOS
```bash
# Shell script with process management
./start_dev.sh

# Interactive script with options
./start.sh
```

### 3. Node.js Unified Script

```bash
# Cross-platform Node.js script
node start.js
```

## Script Features

### start_dev.bat / start_dev_simple.bat
- ✅ Checks for Python, Node.js, and npm
- ✅ Creates virtual environment if needed
- ✅ Installs/updates dependencies
- ✅ Tests backend imports
- ✅ Starts both servers in separate windows
- ✅ Provides helpful URLs and instructions

### start_dev.sh
- ✅ Cross-platform Unix/Linux/macOS support
- ✅ Port availability checking
- ✅ Process management with cleanup
- ✅ Graceful shutdown on Ctrl+C
- ✅ Background process handling

### start.ps1
- ✅ PowerShell-specific features
- ✅ Better error handling
- ✅ Colored output
- ✅ Dependency checking

### start.js
- ✅ Cross-platform Node.js solution
- ✅ Process management
- ✅ Colored console output
- ✅ Graceful shutdown handling

### start.sh (Interactive)
- ✅ Menu-driven interface
- ✅ Multiple start options
- ✅ Platform detection
- ✅ Fallback to existing scripts

## URLs

Once started, the application will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Stop any existing servers
   - Check if ports 3000 and 8000 are free

2. **Python/Node.js not found**
   - Install Python 3.8+ and Node.js 16+
   - Ensure they're in your PATH

3. **Dependencies not installing**
   - Check internet connection
   - Try running with administrator privileges
   - Clear npm cache: `npm cache clean --force`

4. **Backend import errors**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt --upgrade`

### Manual Start

If scripts fail, you can start manually:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
python run_server.py

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## Recommendations

- **Windows users**: Use `start_dev.bat` or `npm start`
- **Unix/Linux/macOS users**: Use `start_dev.sh` or `npm start`
- **Cross-platform**: Use `npm start` or `node start.js`
- **Interactive**: Use `./start.sh` for menu options

All scripts provide the same functionality with different interfaces and error handling approaches.
