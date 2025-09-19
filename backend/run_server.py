#!/usr/bin/env python3
"""
PixelLedger FastAPI Server Runner

This script starts the FastAPI server for the PixelLedger watermarking system.
Make sure to install dependencies first:
    pip install -r requirements.txt

Then run:
    python run_server.py
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting PixelLedger FastAPI Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/api/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
