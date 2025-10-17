"""
Check what extraction parameters work for watermarkedstork.png
"""

import cv2
import sys
sys.path.append('backend')
from app import UltraRobustWatermarkSystem, SemanticWatermarkSystem

# Load image
watermarked = cv2.imread('test_images/watermarkedstork.png')
print("Loaded watermarkedstork.png")
print(f"Size: {watermarked.shape}\n")

print("="*80)
print("TESTING DIFFERENT EXTRACTION METHODS")
print("="*80 + "\n")

# Test 1: UltraRobustWatermarkSystem (what the test script uses)
print("1. UltraRobustWatermarkSystem (delta=60.0):")
system1 = UltraRobustWatermarkSystem(delta=60.0, wavelet='haar', level=2)
result1 = system1.extract(watermarked, "pixel_ledger_2024", fast_mode=False)
if result1.get('success'):
    payload = result1.get('payload', {})
    print(f"   SUCCESS with delta={result1.get('delta_used')}")
    print(f"   Owner: {payload.get('owner')}")
    print(f"   Image ID: {payload.get('image_id')}")
    print(f"   Date: {payload.get('date_created')}\n")
else:
    print("   FAILED\n")

# Test 2: SemanticWatermarkSystem (what the website uses)
print("2. SemanticWatermarkSystem (default delta):")
system2 = SemanticWatermarkSystem()
result2 = system2.extract(watermarked, "pixel_ledger_2024")
if result2.get('success'):
    payload = result2.get('payload', {})
    print(f"   SUCCESS")
    print(f"   Owner: {payload.get('owner')}")
    print(f"   Image ID: {payload.get('image_id')}")
    print(f"   Date: {payload.get('date_created')}\n")
else:
    print("   FAILED\n")

# Test 3: Try different deltas manually
print("3. Testing different delta values manually:")
from backend.watermark_final_working import WatermarkSystem

for delta in [30.0, 40.0, 50.0, 60.0, 70.0, 80.0]:
    system = WatermarkSystem(delta=delta, wavelet='haar', level=2)
    result = system.extract(watermarked, "pixel_ledger_2024")
    
    if result.get('success'):
        payload = result.get('payload', {})
        print(f"   Delta {delta}: SUCCESS")
        print(f"      Owner: {payload.get('owner')}")
        print(f"      Image ID: {payload.get('image_id')}")
        print(f"      Date: {payload.get('date_created')}")
    else:
        print(f"   Delta {delta}: FAILED")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

