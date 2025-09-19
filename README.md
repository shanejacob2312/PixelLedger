# PixelLedger Frontend & Backend

A complete web application for semantic-aware digital watermarking with blockchain binding.

## 🚀 Features

### Frontend (React)
- **Modern Landing Page**: Beautiful, responsive design showcasing PixelLedger capabilities
- **Watermark Creation**: Step-by-step workflow for creating semantic watermarks
- **Watermark Verification**: Upload and verify images for authenticity and tamper detection
- **Image Upload**: Drag-and-drop interface with format validation
- **Metadata Management**: Comprehensive form for ownership and copyright information
- **Real-time Processing**: Live updates during watermark creation and verification
- **Download & Share**: Easy access to watermarked images

### Backend (FastAPI)
- **RESTful API**: Clean, documented API endpoints
- **Image Processing**: Integration with PixelLedger watermarking system
- **File Management**: Secure upload, processing, and serving of images
- **Error Handling**: Comprehensive error handling and validation
- **CORS Support**: Configured for frontend integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│───▶│  FastAPI Backend│───▶│ PixelLedger Core│
│   (Port 3000)  │    │   (Port 8000)  │    │  (Watermarking) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- The PixelLedger watermarking system (in `watermarking/` directory)

### 1. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python run_server.py
```

The backend API will be available at `http://localhost:8000`

### 3. API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - API status
- `GET /api/health` - Health check
- `GET /api/system-info` - System capabilities

### Watermarking Endpoints

- `POST /api/check-watermark` - Check if image has existing watermark
- `POST /api/create-watermark` - Create semantic watermark
- `POST /api/verify-watermark` - Verify watermark authenticity
- `GET /api/download/{filename}` - Download watermarked image

## 🎯 Usage Workflow

### Creating a Watermark

1. **Upload Image**: Select an image file (JPEG, PNG, BMP, TIFF, WebP)
2. **Tamper Check**: System automatically checks for existing watermarks
3. **Add Metadata**: Provide ownership, copyright, and descriptive information
4. **Create Watermark**: AI extracts semantic context and embeds watermark
5. **Download/Share**: Get your watermarked image

### Verifying a Watermark

1. **Upload Image**: Select an image to verify
2. **Extract Watermark**: System extracts embedded watermark data
3. **Verify Authenticity**: Check fingerprint integrity and detect tampering
4. **View Results**: See ownership details and authenticity status

## 🛡️ Security Features

- **Tamper Detection**: Semantic drift analysis detects content changes
- **Format Validation**: Strict file type and size validation
- **Secure Processing**: Temporary file cleanup and secure handling
- **CORS Protection**: Configured for secure cross-origin requests

## 🎨 Frontend Features

### Components
- **LandingPage**: Hero section, features, and call-to-action
- **WatermarkCreate**: Multi-step watermark creation workflow
- **WatermarkVerify**: Image verification and results display
- **Header**: Navigation with active state management

### Styling
- **Tailwind CSS**: Modern, responsive design system
- **Custom Components**: Reusable button, card, and form components
- **Dark/Light Theme**: Consistent color scheme and typography
- **Mobile Responsive**: Optimized for all device sizes

## 🔍 Watermarking Process

### Semantic Context Extraction
- **BLIP Model**: Generates natural language captions
- **ResNet Model**: Detects objects and scenes
- **Perceptual Hashing**: Creates visual fingerprints

### Watermark Embedding
- **LSB Method**: Invisible embedding in blue channel
- **PNG Output**: Preserves watermark integrity
- **Capacity Estimation**: Calculates maximum embeddable data

### Verification Process
- **Fingerprint Validation**: Multi-layer hash verification
- **Drift Detection**: Compares original vs current semantic context
- **Blockchain Ready**: Generates payloads for on-chain storage

## 📁 Project Structure

```
pixel_ledger/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js          # Main app component
│   │   └── index.js        # Entry point
│   ├── public/             # Static assets
│   └── package.json        # Dependencies
├── backend/                # FastAPI backend
│   ├── main.py            # API server
│   ├── run_server.py      # Server runner
│   └── requirements.txt    # Python dependencies
├── watermarking/          # PixelLedger core system
└── README.md              # This file
```

## 🚀 Getting Started

1. **Clone the repository**
2. **Set up the watermarking system** (see `watermarking/README.md`)
3. **Install frontend dependencies**: `cd frontend && npm install`
4. **Install backend dependencies**: `cd backend && pip install -r requirements.txt`
5. **Start the backend**: `cd backend && python run_server.py`
6. **Start the frontend**: `cd frontend && npm start`
7. **Open your browser**: Visit `http://localhost:3000`

## 🔧 Development

### Frontend Development
- Uses React 18 with modern hooks
- Tailwind CSS for styling
- React Router for navigation
- Axios for API calls
- React Hot Toast for notifications

### Backend Development
- FastAPI for high-performance API
- Automatic API documentation
- Type hints and validation
- Async/await support
- CORS middleware

## 📝 License

This project is part of the PixelLedger system. See the main project license for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the watermarking system documentation
- Open an issue in the repository
