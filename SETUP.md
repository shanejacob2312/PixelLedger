# PixelLedger Frontend Setup Guide

## Quick Start

### Option 1: Windows (Recommended)
1. Double-click `start_dev.bat` to start both servers automatically
2. Open your browser to `http://localhost:3000`

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run_server.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Features Implemented

✅ **Landing Page**: Modern, responsive design with feature showcase
✅ **Watermark Creation**: Complete workflow with image upload and metadata form
✅ **Watermark Verification**: Upload and verify images for authenticity
✅ **Image Format Validation**: Supports JPEG, PNG, BMP, TIFF, WebP
✅ **Tamper Detection**: Automatic detection of existing watermarks
✅ **Download/Share**: Easy access to watermarked images
✅ **FastAPI Backend**: RESTful API with comprehensive error handling
✅ **CORS Support**: Configured for frontend integration

## Workflow

### Creating Watermarks
1. Upload image → 2. Check for tampering → 3. Add metadata → 4. Create watermark → 5. Download/Share

### Verifying Watermarks
1. Upload image → 2. Extract watermark → 3. Verify authenticity → 4. View results

## Troubleshooting

- Ensure Python 3.8+ and Node.js 16+ are installed
- Check that ports 3000 and 8000 are available
- Verify the watermarking system is properly set up in the `watermarking/` directory
- Check console logs for any error messages
