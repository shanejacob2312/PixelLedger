"""
Test the new tampering detection system
"""

import cv2
import numpy as np

print("Testing New Tampering Detection System")
print("="*80)

# Test images
test_images = [
    ("test_images/perfect_extreme_showcase/attacked_images/extreme_grayscale.png", "Grayscale"),
    ("test_images/perfect_extreme_showcase/attacked_images/extreme_jpeg_q10.png", "JPEG Q10"),
    ("test_images/perfect_extreme_showcase/attacked_images/extreme_dark_0.4.png", "Dark 0.4x"),
    ("test_images/perfect_extreme_showcase/attacked_images/extreme_combined_jpeg30_dark0.5.png", "Combined JPEG+Dark"),
]

print("\nInstructions:")
print("1. Open your browser to: http://localhost:8000/verify.html")
print("2. Upload each of these test images:")
print()

for path, name in test_images:
    try:
        img = cv2.imread(path)
        if img is not None:
            print(f"   [OK] {name:30s} - {path}")
        else:
            print(f"   [FAIL] {name:30s} - NOT FOUND: {path}")
    except:
        print(f"   [ERROR] {name:30s} - ERROR loading: {path}")

print()
print("3. Expected Results:")
print()
print("   Attack Type           | Tampering Score | Severity      | Tampered |")
print("   ---------------------|-----------------|---------------|----------|")
print("   Grayscale            | 15-25%          | MINOR-MOD     | YES      |")
print("   JPEG Q10             | 30-45%          | MODERATE      | YES      |")
print("   Dark 0.4x            | 20-35%          | MODERATE      | YES      |")
print("   Combined JPEG+Dark   | 45-60%          | MOD-SIG       | YES      |")
print()
print("4. Verify that:")
print("   - Tampering is correctly detected (tampered = true)")
print("   - Tampering score matches expected range")
print("   - Severity classification is shown (MINOR/MODERATE/SIGNIFICANT/SEVERE)")
print("   - Tampering details list specific metrics triggered")
print("   - Original database data is displayed (not corrupted data)")
print()
print("5. Test with original watermarked image:")
print("   - Upload: test_images/watermarkedstork.png")
print("   - Expected: tampered = false, tampering_score = 0")
print()
print("="*80)
print("Backend running at: http://localhost:5000")
print("Frontend running at: http://localhost:8000")
print("Verification page: http://localhost:8000/verify.html")
print("="*80)

