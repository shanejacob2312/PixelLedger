# PixelLedger: Context-Aware Semantic Watermarking with Blockchain Binding

A revolutionary digital image authentication and ownership system that uses **semantic-aware digital watermarking** and **blockchain** to verify content authenticity and ownership.

## 🚀 Core Innovations

### Semantic Watermark
- **Not just owner ID** — embeds image's visual context (object labels, captions, semantic features)
- **Context Embedding** — Uses AI models (BLIP + ResNet) to extract visual labels like "beach", "sunset" and convert to embedded data
- **Blockchain Binding** — Entire watermark structure is hashed and stored on-chain, not just owner ID
- **Self-Verifiable Structure** — Embeds H(image) + H(metadata) + H(features) for comprehensive verification
- **Tamper + Content Drift Detection** — Detects subtle forgery through semantic drift analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Image   │───▶│ Semantic Extract│───▶│  Perceptual Hash│
└─────────────────┘    │   (BLIP+ResNet) │    │   (imagehash)   │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────────┐
                       │     Self-Verifiable Fingerprint        │
                       │  H(image) + H(metadata) + H(features)  │
                       └─────────────────────────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ LSB Watermarking│───▶│ Blockchain Hash │
                       │   (Blue Channel)│    │   (web3.py)     │
                       └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
finalproj/
├── app/
│   ├── core/                    # Core logic modules
│   │   ├── semantic.py          # Semantic feature extraction (BLIP + ResNet)
│   │   ├── phash.py             # Perceptual hash functions
│   │   ├── fingerprint.py       # Self-verifiable fingerprint creation
│   │   ├── lsb_watermark.py     # LSB watermarking functions
│   │   └── pixel_ledger.py      # Main orchestrator
│   ├── api/                     # API route definitions (future)
│   ├── models/                  # Pydantic models/schemas (future)
│   ├── db/                      # Database logic (future)
│   └── utils/                   # Utility functions (future)
├── tests/                       # Unit and integration tests
├── requirements.txt             # Python dependencies
├── test_pixel_ledger.py         # Demo script
└── README.md                    # This file
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finalproj
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python test_pixel_ledger.py
   ```

## 🎯 Usage

### Basic Usage

```python
from app.core.pixel_ledger import PixelLedger

# Initialize the system
ledger = PixelLedger()

# Metadata for the image
metadata = {
    "author": "John Doe",
    "title": "Sunset at the Beach",
    "description": "A beautiful sunset captured at Malibu Beach",
    "creation_date": "2024-01-15",
    "copyright": "© 2024 John Doe. All rights reserved."
}

# Create semantic watermark
result = ledger.create_semantic_watermark(
    image_path="input_image.jpg",
    metadata=metadata,
    output_path="watermarked_image.png"
)

if result["success"]:
    print(f"Semantic Caption: {result['semantic_context']['caption']}")
    print(f"Detected Objects: {result['semantic_context']['detected_objects']}")
    print(f"Blockchain Hash: {result['fingerprint']['blockchain_hash']}")
```

### Verification

```python
# Verify the watermark
verification = ledger.verify_semantic_watermark(
    image_path="watermarked_image.png"
)

if verification["success"]:
    print(f"Fingerprint Valid: {verification['verification_results']['fingerprint_valid']}")
    print(f"Semantic Drift Detected: {verification['drift_analysis']['drift_detected']}")
    print(f"Overall Authentic: {verification['overall_authentic']}")
```

## 🔧 Core Components

### 1. Semantic Extractor (`semantic.py`)
- **BLIP Model**: Generates natural language captions
- **ResNet Model**: Detects objects and scenes (1000 ImageNet classes)
- **Semantic Hash**: Creates hash of semantic features for tamper detection

### 2. Perceptual Hash (`phash.py`)
- Uses `imagehash` library for robust image fingerprinting
- Resistant to minor modifications (compression, resizing)

### 3. Self-Verifiable Fingerprint (`fingerprint.py`)
- **Multi-layer Hashing**: H(image) + H(metadata) + H(features)
- **Blockchain-Ready**: Generates payload for on-chain storage
- **Drift Detection**: Compares original vs current semantic context

### 4. LSB Watermarking (`lsb_watermark.py`)
- **Blue Channel Embedding**: Embeds in blue channel for better invisibility
- **PNG Output**: Automatically saves as PNG to preserve watermark integrity
- **Capacity Estimation**: Calculates maximum embeddable data size
- **Robust Extraction**: Improved error handling and validation

### 5. PixelLedger Orchestrator (`pixel_ledger.py`)
- **End-to-End Workflow**: Combines all components
- **Error Handling**: Robust error management
- **Verification Pipeline**: Complete authenticity verification

## 🔍 Features

### ✅ Implemented
- [x] Semantic context extraction (BLIP + ResNet)
- [x] Perceptual hashing
- [x] Self-verifiable fingerprint creation
- [x] LSB-based watermark embedding/extraction
- [x] Semantic drift detection
- [x] Blockchain-ready payload generation
- [x] Comprehensive verification pipeline

### 🚧 Planned
- [ ] Ethereum blockchain integration (web3.py)
- [ ] FastAPI/Flask backend
- [ ] PostgreSQL/MongoDB database
- [ ] React frontend
- [ ] Docker containerization
- [ ] Unit and integration tests

## 🧪 Testing

Run the demonstration script:
```bash
python test_pixel_ledger.py
```

This will show:
- System capabilities
- Sample metadata structure
- Expected workflow
- Next steps for full implementation

## 🔬 Technical Details

### Semantic Watermarking Process
1. **Extract Semantic Context**: BLIP generates caption, ResNet detects objects
2. **Compute Perceptual Hash**: Create robust image fingerprint
3. **Create Fingerprint**: Combine semantic + hash + metadata with multi-layer hashing
4. **Embed Watermark**: Use LSB to embed fingerprint in blue channel
5. **Generate Blockchain Payload**: Create hash for on-chain storage

### Verification Process
1. **Extract Watermark**: Retrieve embedded fingerprint from LSB
2. **Verify Integrity**: Recompute all hashes and compare
3. **Detect Drift**: Compare original vs current semantic context
4. **Blockchain Verification**: Check against on-chain record (if available)

### Security Features
- **Multi-layer Hashing**: Prevents tampering at any level
- **Semantic Drift Detection**: Catches content modifications
- **Perceptual Hash**: Resistant to compression/resizing
- **LSB Embedding**: Invisible to human eye
- **PNG Preservation**: Lossless format maintains watermark integrity
- **Blockchain Binding**: Immutable ownership record

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **BLIP Model**: Salesforce for image captioning
- **ResNet**: Microsoft Research for object detection
- **LSB Watermarking**: Based on academic research in digital watermarking
- **Blockchain Integration**: Inspired by NFT and digital asset authentication systems

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**PixelLedger**: Where semantic intelligence meets blockchain security for the future of digital image authentication. 🚀 