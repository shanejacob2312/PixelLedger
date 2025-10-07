# PixelLedger - Advanced Invisible Watermarking System

PixelLedger is a comprehensive invisible watermarking system that uses advanced DWT (Discrete Wavelet Transform) techniques, spread-spectrum embedding, and geometric correction to protect digital images with invisible watermarks.

## Features

### Core Watermarking Technology
- **DWT-based Embedding**: Uses 2-level Discrete Wavelet Transform with Daubechies-4 wavelets
- **Spread-Spectrum Technique**: Pseudo-random patterns with 100x replication for robustness
- **Synchronization Template**: Automatic geometric correction for rotation, scaling, and translation
- **Error-Correcting Codes**: BCH(255,127) codes for reliable data recovery
- **High Image Quality**: Maintains PSNR ≥ 35 dB while embedding watermarks

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
- User authentication and profile management
- Image upload and watermark embedding
- Watermark verification and metadata extraction
- Dashboard with statistics and image management
- Responsive design for desktop and mobile

## System Architecture

```
PixelLedger/
├── backend/                 # Backend API and watermarking engine
│   ├── watermark_embed.py   # Watermark embedding module
│   ├── watermark_extract.py # Watermark extraction with geometric correction
│   ├── watermark_test.py    # Attack simulation and evaluation
│   └── app.py              # Flask REST API server
├── frontend/               # Web application frontend
│   ├── index.html          # Landing page
│   ├── login.html          # User login
│   ├── signup.html         # User registration
│   └── dashboard.html      # Main application dashboard
├── demo.ipynb              # Interactive demonstration notebook
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- 4GB RAM minimum (8GB recommended)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pixelledgerdwt
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   cd backend
   python app.py
   ```
   The database will be created automatically on first run.

5. **Start the backend server**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Open the frontend**
   - Navigate to the `frontend/` directory
   - Open `index.html` in your web browser
   - Or serve it using a local web server:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
     Then visit `http://localhost:8080`

## Usage

### Web Application

1. **Landing Page**: Visit the homepage to learn about PixelLedger's features
2. **Registration**: Create a new account with username, email, and password
3. **Login**: Sign in to access the dashboard
4. **Watermark Images**: 
   - Upload an image
   - Fill in metadata (owner, creator, copyright, etc.)
   - Download the watermarked image
5. **Verify Watermarks**: Upload any image to check for embedded watermarks

### Python API

```python
from backend.watermark_embed import WatermarkEmbedder
from backend.watermark_extract import WatermarkExtractor

# Initialize embedder
embedder = WatermarkEmbedder(
    dwt_levels=2,
    wavelet='db4',
    replication_factor=100,
    embedding_strength=0.08,
    payload_size=128
)

# Embed watermark
payload_data = {
    'owner': 'John Doe',
    'creator': 'Jane Smith',
    'date_created': '2024-01-15',
    'copyright': '© 2024 PixelLedger'
}

watermarked_image, metadata = embedder.embed_watermark(
    original_image, payload_data, secret_key
)

# Extract watermark
extractor = WatermarkExtractor()
results = extractor.extract_with_geometric_correction(
    watermarked_image, secret_key, original_image
)
```

### Demo Notebook

Run the interactive demo:
```bash
jupyter notebook demo.ipynb
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
| Wavelet | db4 | Daubechies-4 wavelet basis |
| Replication Factor | 100 | Number of replications per bit |
| Embedding Strength | 0.08 | Watermark embedding strength |
| Payload Size | 128 bits | Size of embedded data |
| ECC Codes | BCH(255,127) | Error-correcting code parameters |

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

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd backend
   python -c "import watermark_embed"
   ```

2. **Database Errors**
   ```bash
   # Delete the database file and restart
   rm pixelledger.db
   python app.py
   ```

3. **Frontend Not Loading**
   - Check if backend is running on port 5000
   - Verify API_BASE_URL in frontend JavaScript
   - Check browser console for errors

4. **Watermark Embedding Fails**
   - Ensure image is in supported format (PNG, JPG, JPEG)
   - Check image size (max 16MB)
   - Verify all required metadata fields are provided

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

- **v1.0.0** - Initial release with core watermarking functionality
- **v1.1.0** - Added geometric correction and web interface
- **v1.2.0** - Enhanced robustness and performance optimization
- **v1.3.0** - MongoDB integration for scalable user management
- **v2.0.0** - Blockchain integration for immutable hash verification (Planned)

---

**PixelLedger** - Protecting your digital images with advanced invisible watermarking technology.
