#!/bin/bash

# PixelLedger Cross-Platform Start Script
# This script provides a simple way to start both frontend and backend

echo "🚀 PixelLedger Development Environment"
echo "======================================"
echo ""
echo "Choose your start method:"
echo "1. Use existing scripts (recommended)"
echo "2. Use Node.js unified script"
echo "3. Start backend only"
echo "4. Start frontend only"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Using existing start scripts..."
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            echo "Windows detected - using batch script"
            if [ -f "start_dev.bat" ]; then
                ./start_dev.bat
            else
                echo "❌ start_dev.bat not found"
                exit 1
            fi
        else
            echo "Unix/Linux detected - using shell script"
            if [ -f "start_dev.sh" ]; then
                chmod +x start_dev.sh
                ./start_dev.sh
            else
                echo "❌ start_dev.sh not found"
                exit 1
            fi
        fi
        ;;
    2)
        echo "Using Node.js unified script..."
        if command -v node &> /dev/null; then
            node start.js
        else
            echo "❌ Node.js not found. Please install Node.js first."
            exit 1
        fi
        ;;
    3)
        echo "Starting backend only..."
        cd backend
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            call venv\Scripts\activate.bat && python run_server.py
        else
            source venv/bin/activate && python run_server.py
        fi
        ;;
    4)
        echo "Starting frontend only..."
        cd frontend
        npm start
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
