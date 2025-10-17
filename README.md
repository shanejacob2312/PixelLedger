
# PixelLedger - Advanced Invisible Watermarking System

PixelLedger is a comprehensive invisible watermarking system that uses advanced DWT (Discrete Wavelet Transform) techniques, AI-powered semantic analysis, and cryptographic fingerprinting to protect digital images with invisible watermarks.

## Features

### Core Watermarking Technology
- **DWT-based Embedding**: Uses 2-level Discrete Wavelet Transform with Haar wavelets
- **Quantization-based Technique**: Robust coefficient modification for reliable embedding
- **High Image Quality**: Maintains PSNR ≥ 35 dB while embedding watermarks
- **Geometric Robustness**: Resistant to rotation, scaling, cropping, and compression

### Semantic Watermarking (AI-Powered)
- **BLIP Caption Generation**: AI-generated natural language descriptions of image content
- **ResNet Object Detection**: Top-5 object/scene classification with confidence scores
- **Semantic Hash Creation**: SHA256 hash of semantic content for tamper detection
- **Perceptual Hashing**: Visual fingerprint resistant to compression/resizing
- **Multi-Layer Fingerprinting**: H(image), H(metadata), H(features), H(fingerprint)
- **Blockchain-Ready Payload**: Essential verification data prepared for on-chain storage

### Future Blockchain Integration (v2.0)
- **Cryptographic Hash Storage**: Watermark metadata hashes stored on blockchain
- **Immutable Verification**: Tamper-proof ownership verification via smart contracts
- **Decentralized Security**: No single point of failure for verification
- **Public Transparency**: Blockchain-based ownership records
- **Web3 Ready**: Prepared for decentralized applications

### Robustness Against Attacks
- JPEG compression (quality 30-90)
- Gaussian noise (σ=2-10)
- Cropping (5-30% removal)
- Rotation (±15°)
- Scaling (0.5×-2×)
- Combined attacks

### Web Application Features
- **User Authentication**: Secure JWT-based authentication with session management
- **Watermark Embedding**: Upload images and embed invisible watermarks with metadata
- **Semantic Analysis Display**: View AI-generated captions and detected objects
- **Cryptographic Hashes**: View embedded semantic, perceptual, and master fingerprint hashes
- **Watermark Verification**: Upload any image to detect and extract watermarks
- **Advanced Tamper Detection**: Identify if watermarked images have been modified with confidence scores
- **Original Data Display**: Shows original database details for tampered images (not corrupted extraction)
- **Double-Watermark Prevention**: Blocks re-watermarking of already watermarked images (clean or tampered)
- **Ultra-Robust Extraction**: Multiple delta value strategy (20.0 to 80.0) with advanced error correction
- **Dashboard**: Statistics, image gallery, and recent activity
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## System Architecture

```
PixelLedger/
├── backend/                          # Backend API and watermarking engine
│   ├── app.py                        # Flask REST API server with MongoDB
│   ├── watermark_final_working.py    # Core DWT watermarking system
│   ├── semantic_watermark.py         # AI-powered semantic watermarking
│   └── flask_session/                # Session storage
├── frontend/                         # Web application frontend
│   ├── index.html                    # Landing page
│   ├── login.html                    # User login
│   ├── signup.html                   # User registration
│   ├── dashboard.html                # Main dashboard with stats
│   ├── watermark.html                # Watermark embedding interface
│   ├── verify.html                   # Watermark verification interface
│   └── images/                       # UI assets
├── test_images/                      # Test images and results
│   ├── original/                     # Original test images
│   ├── watermarked/                  # Watermarked outputs
│   └── attacked/                     # Attack simulation results
├── requirements.txt                  # Python dependencies
├── BLOCKCHAIN_ROADMAP.md             # Blockchain integration plan
└── README.md                         # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or MongoDB Atlas)
- Modern web browser
- 4GB RAM minimum (8GB recommended for AI features)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pixledgerdwt
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB**
   - Install MongoDB locally, OR
   - Update `MONGODB_URI` in `backend/app.py` with your MongoDB Atlas connection string

4. **Launch Backend Server**
   ```bash
   cd backend
   python app.py
   ```
   The API will be available at `http://localhost:5000`

5. **Launch Frontend Server**
   
   **Option 1: Python HTTP Server (Recommended - No auto-refresh issues)**
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then visit `http://localhost:8080`

   **Option 2: Live Server (VS Code Extension)**
   - Install Live Server extension in VS Code
   - Right-click `frontend/index.html` → "Open with Live Server"
   - Visit `http://localhost:5500`
   
   **Note:** If using Live Server, disable auto-refresh to prevent interruptions during watermarking.

6. **Access the Application**
   - Landing Page: `http://localhost:8080/index.html`
   - Sign Up: `http://localhost:8080/signup.html`
   - Login: `http://localhost:8080/login.html`
   - Dashboard: `http://localhost:8080/dashboard.html` (after login)
   - Watermark: `http://localhost:8080/watermark.html` (after login)
   - Verify: `http://localhost:8080/verify.html` (after login)

## Usage

### Web Application Workflow

1. **Registration & Login**
   - Create account at `/signup.html`
   - Login at `/login.html`
   - JWT token stored in localStorage for authentication

2. **Watermark Images** (`/watermark.html`)
   - Upload an image (PNG, JPG, JPEG - max 16MB)
   - Fill in metadata:
     - Owner/Copyright Holder (required)
     - Creator/Artist (required)
     - Date Created (required)
     - Work Title (required)
     - Copyright Information (optional)
     - Description, Medium, Category (optional)
   - AI Analysis automatically generates:
     - Natural language caption (BLIP)
     - Object detection with confidence scores (ResNet)
     - Semantic hash for content verification
     - Perceptual hash for visual fingerprint
     - Master fingerprint for blockchain
   - View embedded data and cryptographic hashes
   - Download watermarked image
   - Share on social media or copy to clipboard

3. **Verify Watermarks** (`/verify.html`)
   - Upload any image to check for watermarks
   - Three possible results:
     - ✅ **Watermark Verified**: Shows all embedded metadata, AI analysis, and hashes
     - ⚠️ **Image Tampered**: Watermark detected but image was modified
     - ❌ **No Watermark**: No watermark detected in image
   - View database record matches
   - See semantic features and fingerprints

4. **Dashboard** (`/dashboard.html`)
   - View statistics (images watermarked, verifications performed)
   - Browse watermarked images gallery
   - Quick access to watermark and verify tools

### Python API

```python
from backend.semantic_watermark import SemanticWatermarkSystem
import cv2
import numpy as np

# Initialize semantic watermarking system
watermark_system = SemanticWatermarkSystem(
    delta=60.0,        # Embedding strength
    wavelet='haar',    # Wavelet type
    level=2           # DWT decomposition levels
)

# Load image
image = cv2.imread('original.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Prepare payload
payload = {
    'owner': 'John Doe',
    'creator': 'Jane Smith',
    'date_created': '2024-01-15',
    'image_id': 'img-12345'
}

# Embed watermark with AI analysis
secret_key = 'your-secret-key'
watermarked_image, metadata = watermark_system.embed(image, payload, secret_key)

# Metadata includes:
# - AI-generated caption (BLIP)
# - Detected objects with confidence (ResNet)
# - Semantic hash (SHA256 of semantic content)
# - Perceptual hash (visual fingerprint)
# - Multi-layer cryptographic fingerprint
# - Blockchain-ready payload
# - PSNR quality metric

# Extract watermark
extraction_result = watermark_system.extract(watermarked_image, secret_key)

if extraction_result['success']:
    print("Extracted payload:", extraction_result['payload'])
    print("Semantic hash:", extraction_result['payload']['semantic_hash'])
    print("Master fingerprint:", extraction_result['payload']['master_fingerprint'])
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile

### Watermarking
- `POST /api/watermark/embed` - Embed watermark in image
- `POST /api/watermark/verify` - Verify watermark in image

### Image Management
- `GET /api/images` - Get user's watermarked images
- `GET /api/images/<id>` - Get specific image
- `GET /api/images/<id>/download` - Download watermarked image

### Statistics
- `GET /api/stats` - Get user statistics

## Configuration Parameters

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| DWT Levels | 2 | Number of wavelet decomposition levels |
| Wavelet | haar | Haar wavelet basis |
| Delta (Embedding Strength) | 60.0 | Quantization step size for embedding |
| Payload Size | ~120 chars | Embedded text payload (owner, image_id, date, hashes) |
| Hash Size | 16 chars | Truncated hash sizes for reliable embedding |
| AI Models | BLIP, ResNet-50 | Semantic analysis models |

## Performance Metrics

The system provides comprehensive evaluation metrics:

- **PSNR**: Peak Signal-to-Noise Ratio (target: ≥35 dB)
- **SSIM**: Structural Similarity Index
- **Bit Error Rate**: Percentage of incorrectly extracted bits
- **Correlation Score**: Template and payload correlation
- **Detection Success Rate**: Percentage of successful extractions
- **Extraction Time**: Time required for watermark extraction

## Security Features

- **Secret Key Protection**: Watermarks are generated using secret keys
- **Pseudo-Random Patterns**: Cryptographically secure pattern generation
- **Error Correction**: BCH codes prevent data corruption
- **Geometric Correction**: Robust against geometric attacks
- **Session Management**: Secure user authentication

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## System Requirements

### Backend
- Python 3.8+
- 2GB RAM minimum
- 500MB disk space

### Frontend
- Modern web browser
- JavaScript enabled
- 100MB available memory

## Troubleshooting

### Common Issues

1. **Page Resets After Watermarking**
   - **Cause**: Live Server auto-refresh
   - **Solution**: Use Python HTTP server instead:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Or disable Live Server auto-refresh in VS Code settings

2. **CORS Errors**
   - **Error**: "Access to fetch... has been blocked by CORS policy"
   - **Solution**: Ensure CORS origins in `backend/app.py` include your frontend URL:
     ```python
     origins=['http://localhost:8080', 'http://127.0.0.1:8080', ...]
     ```
   - Restart backend after changes

3. **MongoDB Connection Failed**
   - Check MongoDB is running: `mongod --version`
   - Update `MONGODB_URI` in `backend/app.py`
   - For MongoDB Atlas, ensure IP whitelist is configured

4. **AI Models Not Loading**
   - Install PyTorch: `pip install torch torchvision`
   - Install Transformers: `pip install transformers`
   - First run will download models (~2GB) - be patient
   - Check disk space (need ~5GB free)

5. **Watermark Extraction Loops Infinitely**
   - **Fixed**: Backend now stops after first match
   - Restart backend to apply fix

6. **Session/Authentication Issues**
   - Clear browser localStorage
   - Delete cookies for localhost
   - Re-login to get fresh JWT token
   - Check token exists: `localStorage.getItem('pixelledger_token')`

7. **Image Upload Fails**
   - Check image format (PNG, JPG, JPEG only)
   - Max file size: 16MB
   - Verify all required fields are filled
   - Check browser console for errors

### Performance Optimization

1. **For Large Images**
   - Reduce embedding strength for faster processing
   - Use smaller replication factor for less robust but faster embedding

2. **For Better Robustness**
   - Increase replication factor
   - Use stronger embedding strength
   - Enable all geometric correction features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Blockchain Integration Roadmap

PixelLedger v2.0 will introduce blockchain integration for enhanced security:

### Key Features (Planned)
- **Hash-based Verification**: Cryptographic hashes of watermark metadata stored on blockchain
- **Immutable Records**: Tamper-proof ownership verification via smart contracts
- **Decentralized Security**: No single point of failure
- **Public Transparency**: Blockchain-based ownership records

### Implementation Timeline
- **Q1 2024**: Hash generation and smart contract development
- **Q2 2024**: Backend blockchain integration
- **Q3 2024**: Frontend enhancement and testing
- **Q4 2024**: Production deployment

For detailed blockchain integration plans, see [BLOCKCHAIN_ROADMAP.md](BLOCKCHAIN_ROADMAP.md).

## Support

For support and questions:
- Email: support@pixelledger.com
- Documentation: [Link to documentation]
- Issues: [GitHub Issues]

## Acknowledgments

- PyWavelets library for DWT implementation
- OpenCV for image processing
- Flask for web framework
- BCH library for error correction

## Version History

- **v1.0.0** - Initial release with core DWT watermarking functionality
- **v1.1.0** - Added web interface and user authentication
- **v1.2.0** - Enhanced robustness and MongoDB integration
- **v1.3.0** - Semantic watermarking with AI (BLIP + ResNet)
- **v1.4.0** - Cryptographic fingerprinting and multi-layer hashing (Current)
- **v2.0.0** - Blockchain integration for immutable hash verification (Planned Q4 2024)

---

**PixelLedger** - Protecting your digital images with advanced invisible watermarking technology.
