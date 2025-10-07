# PixelLedger Testing System

This directory contains the comprehensive testing system for PixelLedger watermarking technology.

## Directory Structure

```
test_images/
├── original/          # Place your original test images here
├── watermarked/       # Generated watermarked images
├── attacked/          # Generated attacked versions
├── results/           # Test results, reports, and logs
└── README.md         # This file
```

## How to Use

### 1. Add Test Images
Place your original images in the `original/` directory. Supported formats:
- JPG/JPEG
- PNG
- BMP
- TIFF
- GIF

### 2. Run the Test
```bash
python test_pixelledger_workflow.py
```

### 3. Review Results
Check the `results/` directory for:
- `test_log.txt` - Detailed execution logs
- `detailed_report.json` - Complete test results in JSON format
- `performance_analysis.png` - Performance visualization plots

## What the Test Does

### Phase 1: Watermark Embedding
- Loads all images from `original/`
- Embeds invisible watermarks with test metadata
- Calculates PSNR (Peak Signal-to-Noise Ratio)
- Measures embedding time
- Saves watermarked images to `watermarked/`

### Phase 2: Watermark Verification
- Verifies watermarks on all watermarked images
- Extracts embedded metadata
- Calculates confidence scores
- Measures extraction time

### Phase 3: Attack Simulation
Creates various attacked versions of watermarked images:

#### Image Quality Attacks:
- **JPEG Compression**: Quality levels 80, 60, 40
- **Gaussian Noise**: Adds random noise

#### Geometric Attacks:
- **Rotation**: 5°, 10°, 15° rotations
- **Scaling**: 0.8x, 1.2x, 0.5x scaling
- **Cropping**: 10%, 20%, 30% cropping

#### Combined Attacks:
- **Combined**: JPEG + Rotation + Noise

### Phase 4: Attack Testing
- Verifies watermarks on all attacked images
- Determines which attacks the watermark survives
- Calculates survival rates for each attack type

## Test Metadata

Each image is watermarked with the following test data:
```json
{
    "owner": "Test Owner X",
    "creator": "Test Artist X", 
    "date_created": "2025-01-05",
    "copyright": "Test Copyright 2025",
    "title": "Test Artwork X",
    "description": "Test artwork for PixelLedger testing",
    "medium": "Digital Art",
    "category": "Test"
}
```

## Performance Metrics

The test measures:
- **PSNR**: Image quality preservation (higher is better)
- **Confidence**: Watermark detection confidence (0-1, higher is better)
- **Processing Time**: Embedding and extraction speed
- **Survival Rate**: Percentage of attacks the watermark survives

## Expected Results

For a robust watermarking system, you should see:
- **PSNR > 30 dB**: Good image quality preservation
- **Confidence > 0.7**: Reliable watermark detection
- **High survival rates**: Watermark survives most attacks
- **Fast processing**: < 1 second for typical images

## Troubleshooting

### No Images Found
- Ensure images are in `test_images/original/`
- Check file extensions (JPG, PNG, BMP, TIFF, GIF)
- Verify file permissions

### Backend Connection Issues
- Make sure the backend server is running: `python backend/app_mongodb.py`
- Check if the server is accessible at `http://localhost:5000`

### Memory Issues
- Reduce image sizes if processing large files
- Process fewer images at once
- Ensure sufficient RAM available

## Advanced Usage

### Custom Test Parameters
Edit `test_pixelledger_workflow.py` to modify:
- Watermarking parameters (strength, replication factor)
- Attack parameters (noise levels, rotation angles)
- Test metadata

### Batch Processing
The system automatically processes all images in the `original/` directory. Add multiple images for comprehensive testing.

### Result Analysis
Use the generated JSON report for detailed analysis:
```python
import json
with open('test_images/results/detailed_report.json') as f:
    results = json.load(f)
    # Analyze results programmatically
```

## Support

For issues or questions about the testing system, check:
1. The test log: `test_images/results/test_log.txt`
2. Backend logs in the terminal
3. PixelLedger documentation

---

**Note**: This testing system uses the local watermarking modules directly for comprehensive testing. For web interface testing, use the frontend at `http://localhost:5500/frontend/`.
