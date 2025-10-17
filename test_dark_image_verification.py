"""
Test verification with extreme_dark_0.4 image to debug tampering detection
"""

import cv2
import numpy as np
import sys
import os

sys.path.append('backend')

# Load the attacked image
attacked_path = "test_images/perfect_extreme_showcase/attacked_images/extreme_dark_0.4.png"
print(f"Loading attacked image: {attacked_path}")
attacked_image = cv2.imread(attacked_path)
attacked_image = cv2.cvtColor(attacked_image, cv2.COLOR_BGR2RGB)
print(f"Attacked image shape: {attacked_image.shape}\n")

# Load the original watermarked image
original_path = "test_images/watermarkedstork.png"
print(f"Loading original watermarked image: {original_path}")
original_image = cv2.imread(original_path)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
print(f"Original image shape: {original_image.shape}\n")

# Resize if needed
if attacked_image.shape != original_image.shape:
    print(f"Resizing attacked image to match original...")
    attacked_image = cv2.resize(attacked_image, (original_image.shape[1], original_image.shape[0]))
    print(f"New attacked image shape: {attacked_image.shape}\n")

print("="*80)
print("TAMPERING DETECTION METRICS")
print("="*80 + "\n")

# METRIC 1: Perceptual Hash
print("1. Perceptual Hash Distance:")
try:
    import imagehash
    from PIL import Image
    
    attacked_pil = Image.fromarray(attacked_image)
    original_pil = Image.fromarray(original_image)
    
    attacked_phash = imagehash.phash(attacked_pil)
    original_phash = imagehash.phash(original_pil)
    hamming_distance = attacked_phash - original_phash
    
    print(f"   Hamming Distance: {hamming_distance}")
    print(f"   Threshold: > 5 indicates tampering")
    print(f"   Result: {'TAMPERED' if hamming_distance > 5 else 'CLEAN'}")
    print(f"   Contribution: {min(hamming_distance * 5, 40)}/40 points\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

# METRIC 2: SSIM
print("2. Structural Similarity (SSIM):")
try:
    from skimage.metrics import structural_similarity as ssim
    
    attacked_gray = cv2.cvtColor(attacked_image, cv2.COLOR_RGB2GRAY)
    original_gray = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
    
    ssim_score = ssim(attacked_gray, original_gray)
    print(f"   SSIM Score: {ssim_score:.6f}")
    print(f"   Threshold: < 0.95 indicates tampering")
    print(f"   Result: {'TAMPERED' if ssim_score < 0.95 else 'CLEAN'}")
    ssim_penalty = (1.0 - ssim_score) * 100
    print(f"   Contribution: {min(ssim_penalty, 30):.2f}/30 points\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

# METRIC 3: MSE
print("3. Mean Squared Error (MSE):")
try:
    mse = np.mean((attacked_image.astype(float) - original_image.astype(float)) ** 2)
    print(f"   MSE: {mse:.2f}")
    print(f"   Threshold: > 100 indicates tampering")
    print(f"   Result: {'TAMPERED' if mse > 100 else 'CLEAN'}")
    mse_penalty = min(mse / 10, 20)
    print(f"   Contribution: {mse_penalty:.2f}/20 points\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

# METRIC 4: Histogram
print("4. Histogram Correlation:")
try:
    hist_correlation = 0
    for channel in range(3):
        hist_attacked = cv2.calcHist([attacked_image], [channel], None, [256], [0, 256])
        hist_original = cv2.calcHist([original_image], [channel], None, [256], [0, 256])
        
        hist_attacked = cv2.normalize(hist_attacked, hist_attacked).flatten()
        hist_original = cv2.normalize(hist_original, hist_original).flatten()
        
        correlation = cv2.compareHist(hist_attacked, hist_original, cv2.HISTCMP_CORREL)
        hist_correlation += correlation
    
    hist_correlation /= 3
    print(f"   Histogram Correlation: {hist_correlation:.6f}")
    print(f"   Threshold: < 0.95 indicates tampering")
    print(f"   Result: {'TAMPERED' if hist_correlation < 0.95 else 'CLEAN'}")
    hist_penalty = (1.0 - hist_correlation) * 100
    print(f"   Contribution: {min(hist_penalty, 10):.2f}/10 points\n")
except Exception as e:
    print(f"   ERROR: {e}\n")

# Calculate total tampering score
print("="*80)
print("TOTAL TAMPERING ANALYSIS")
print("="*80 + "\n")

tampering_score = 0
tampered = False
details = []

# Recalculate with all metrics
try:
    if hamming_distance > 5:
        tampered = True
        score_contrib = min(hamming_distance * 5, 40)
        tampering_score += score_contrib
        details.append(f"Visual structure modified (phash distance: {hamming_distance})")
        print(f"[PHASH] Tampered! Score += {score_contrib:.1f}")
except:
    pass

try:
    if ssim_score < 0.95:
        tampered = True
        ssim_penalty = (1.0 - ssim_score) * 100
        score_contrib = min(ssim_penalty, 30)
        tampering_score += score_contrib
        details.append(f"Structural changes detected (SSIM: {ssim_score:.3f})")
        print(f"[SSIM] Tampered! Score += {score_contrib:.1f}")
except:
    pass

try:
    if mse > 100:
        tampered = True
        score_contrib = min(mse / 10, 20)
        tampering_score += score_contrib
        details.append(f"Pixel-level modifications detected (MSE: {mse:.1f})")
        print(f"[MSE] Tampered! Score += {score_contrib:.1f}")
except:
    pass

try:
    if hist_correlation < 0.95:
        tampered = True
        hist_penalty = (1.0 - hist_correlation) * 100
        score_contrib = min(hist_penalty, 10)
        tampering_score += score_contrib
        details.append(f"Color/brightness modified (histogram: {hist_correlation:.3f})")
        print(f"[HISTOGRAM] Tampered! Score += {score_contrib:.1f}")
except:
    pass

print(f"\nFinal Tampering Score: {tampering_score:.1f}/100")
print(f"Tampered: {tampered}")
print(f"\nTampering Details:")
for detail in details:
    print(f"  - {detail}")

# Severity classification
if tampering_score < 20:
    severity = "MINOR"
elif tampering_score < 50:
    severity = "MODERATE"
elif tampering_score < 75:
    severity = "SIGNIFICANT"
else:
    severity = "SEVERE"

print(f"\nSeverity: {severity}")
print(f"Confidence Score: {max(30, 100 - tampering_score):.1f}%")

print("\n" + "="*80)
print("EXPECTED BEHAVIOR:")
print("  - Dark 0.4x should show TAMPERED = True")
print("  - Tampering Score should be 20-35%")
print("  - Severity should be MODERATE")
print("="*80)

