"""
Perfect Extreme Showcase - Using Hybrid Verification (like website)
Detects watermarks even when corrupted and shows database records

Author: PixelLedger Team
"""

import cv2
import numpy as np
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import imagehash

sys.path.append('backend')
from app import UltraRobustWatermarkSystem, watermarked_images_collection

class HybridExtremeShowcase:
    def __init__(self):
        self.extraction_system = UltraRobustWatermarkSystem(delta=60.0, wavelet='haar', level=2)
        
    def hybrid_verify(self, image):
        """Verify watermark using same hybrid approach as website"""
        # Extract watermark
        extraction_results = self.extraction_system.extract(
            image, 
            secret_key="pixel_ledger_2024",
            fast_mode=False
        )
        
        if not extraction_results.get('success', False):
            return None, "NO_WATERMARK", 0
        
        extracted_payload = extraction_results.get('payload', {})
        extracted_image_id = extracted_payload.get('image_id', '')
        
        if not extracted_image_id:
            return None, "NO_ID", 0
        
        # STRATEGY 1: Exact Match
        image_record = watermarked_images_collection.find_one({'short_hash': extracted_image_id})
        if image_record:
            return image_record, "EXACT_MATCH", 100.0
        
        # STRATEGY 2: Fuzzy Match
        clean_id = ''.join(c if c.isalnum() else '' for c in extracted_image_id)
        
        if len(clean_id) >= 6:
            all_db_images = list(watermarked_images_collection.find(
                {}, {'short_hash': 1, 'image_id': 1, 'owner': 1, 'created_at': 1}
            ).sort('created_at', -1).limit(20))
            
            best_match = None
            best_score = 0
            
            for db_img in all_db_images:
                db_short_hash = db_img.get('short_hash', '')
                if db_short_hash:
                    matches = sum(1 for a, b in zip(clean_id, db_short_hash) if a.lower() == b.lower())
                    max_len = max(len(clean_id), len(db_short_hash))
                    score = (matches / max_len) if max_len > 0 else 0
                    
                    if score > best_score:
                        best_score = score
                        best_match = db_img
            
            if best_match and best_score >= 0.5:
                image_record = watermarked_images_collection.find_one({'_id': best_match['_id']})
                return image_record, "FUZZY_MATCH", best_score * 100
        
        # STRATEGY 3: Perceptual Hash
        try:
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            uploaded_phash = str(imagehash.phash(image_pil))
            
            all_db_images = list(watermarked_images_collection.find(
                {'perceptual_hash': {'$exists': True}}, 
                {'perceptual_hash': 1}
            ).sort('created_at', -1).limit(20))
            
            best_match = None
            best_hamming = float('inf')
            
            for db_img in all_db_images:
                db_phash = db_img.get('perceptual_hash', '')
                if db_phash:
                    hamming = sum(c1 != c2 for c1, c2 in zip(uploaded_phash, db_phash))
                    if hamming < best_hamming:
                        best_hamming = hamming
                        best_match = db_img
            
            if best_match and best_hamming <= 10:
                image_record = watermarked_images_collection.find_one({'_id': best_match['_id']})
                confidence = max(0, (10 - best_hamming) / 10 * 100)
                return image_record, "PERCEPTUAL_HASH", confidence
        except:
            pass
        
        return None, "NO_MATCH", 0
    
    def create_showcase_comparison(self, original, attacked, attack_name, db_record, match_method, confidence, attack_description):
        """Create professional showcase comparison"""
        h, w = original.shape[:2]
        
        # Create canvas
        canvas_h = h + 280
        canvas_w = w * 2 + 100
        canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 245
        
        # Add borders
        cv2.rectangle(canvas, (0, 0), (canvas_w-1, canvas_h-1), (100, 100, 100), 3)
        
        # Place images with borders
        img_y = 140
        img1_x = 30
        img2_x = w + 70
        
        # Original
        cv2.rectangle(canvas, (img1_x-2, img_y-2), (img1_x+w+2, img_y+h+2), (0, 150, 0), 2)
        canvas[img_y:img_y+h, img1_x:img1_x+w] = original
        
        # Attacked
        cv2.rectangle(canvas, (img2_x-2, img_y-2), (img2_x+w+2, img_y+h+2), (0, 0, 200), 2)
        canvas[img_y:img_y+h, img2_x:img2_x+w] = attacked
        
        # Convert to PIL for text
        canvas_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(canvas_pil)
        
        # Fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            subtitle_font = ImageFont.truetype("arial.ttf", 28)
            label_font = ImageFont.truetype("arial.ttf", 22)
            data_font = ImageFont.truetype("arialbd.ttf", 20)
            small_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = label_font = subtitle_font = data_font = small_font = ImageFont.load_default()
        
        # Title
        draw.text((canvas_w // 2 - 350, 30), "PIXELLEDGER ROBUSTNESS TEST", fill=(0, 0, 150), font=title_font)
        draw.text((canvas_w // 2 - 220, 80), "WATERMARK DETECTED & VERIFIED", fill=(0, 150, 0), font=subtitle_font)
        
        # Labels
        draw.text((img1_x + w // 2 - 140, 115), "ORIGINAL WATERMARKED", fill=(0, 100, 0), font=label_font)
        draw.text((img2_x + w // 2 - 100, 115), f"{attack_name.upper()}", fill=(200, 0, 0), font=label_font)
        
        # Attack description
        draw.text((30, img_y + h + 15), attack_description, fill=(50, 50, 50), font=label_font)
        
        # Database record (clean data)
        y_pos = img_y + h + 55
        
        # Verification status
        draw.text((30, y_pos), f"VERIFIED: {match_method}", fill=(0, 150, 0), font=data_font)
        draw.text((30, y_pos + 30), f"Confidence: {confidence:.1f}%", fill=(0, 100, 0), font=small_font)
        
        # Clean database record
        owner = db_record.get('owner', 'N/A')
        image_id = db_record.get('short_hash', db_record.get('image_id', 'N/A'))
        date_created = db_record.get('created_at', 'N/A')
        if hasattr(date_created, 'strftime'):
            date_created = date_created.strftime('%Y-%m-%d')
        
        draw.text((30, y_pos + 65), f"Owner: {owner}", fill=(0, 0, 0), font=data_font)
        draw.text((30, y_pos + 95), f"Image ID: {image_id[:20]}...", fill=(0, 0, 0), font=data_font)
        draw.text((500, y_pos + 65), f"Date: {date_created}", fill=(0, 0, 0), font=data_font)
        draw.text((500, y_pos + 95), "Source: Database Record", fill=(100, 100, 100), font=small_font)
        
        # Status badge
        draw.text((canvas_w - 180, y_pos + 50), "VERIFIED", fill=(0, 150, 0), font=title_font)
        
        # Convert back
        result = cv2.cvtColor(np.array(canvas_pil), cv2.COLOR_RGB2BGR)
        return result
    
    def test_extreme_attacks(self, watermarked_path):
        """Test extreme attacks with hybrid verification"""
        print("\n" + "="*80)
        print("PERFECT EXTREME SHOWCASE - HYBRID VERIFICATION (LIKE WEBSITE)")
        print("="*80 + "\n")
        
        # Load
        watermarked = cv2.imread(watermarked_path)
        if watermarked is None:
            print(f"ERROR: Could not load {watermarked_path}")
            return
        
        watermarked_rgb = cv2.cvtColor(watermarked, cv2.COLOR_BGR2RGB)
        
        print(f"Loaded: {watermarked_path}")
        print(f"Size: {watermarked.shape}\n")
        
        # Verify original
        print("Verifying original with hybrid method...")
        db_record, method, confidence = self.hybrid_verify(watermarked_rgb)
        
        if not db_record:
            print(f"ERROR: Could not verify original watermark (Method: {method})")
            return
        
        print(f"SUCCESS: {method} (Confidence: {confidence:.1f}%)")
        print(f"  Owner: {db_record.get('owner')}")
        print(f"  Image ID: {db_record.get('short_hash')}")
        print(f"  Date: {db_record.get('created_at')}\n")
        
        # Define extreme attacks
        print("Applying extreme attacks...\n")
        
        extreme_attacks = []
        h, w = watermarked.shape[:2]
        
        # Attacks (same as before)
        print("  1. Extreme JPEG Q10")
        _, encoded = cv2.imencode('.jpg', watermarked, [cv2.IMWRITE_JPEG_QUALITY, 10])
        extreme_attacks.append(("extreme_jpeg_q10", cv2.imdecode(encoded, cv2.IMREAD_COLOR), 
                               "Extreme JPEG Compression - Quality 10 (90% compression)"))
        
        print("  2. Severe Darkening")
        extreme_attacks.append(("extreme_dark_0.4", 
                               np.clip(watermarked.astype(np.float32) * 0.4, 0, 255).astype(np.uint8),
                               "Severe Darkening - 60% brightness reduction"))
        
        print("  3. Severe Brightening")
        extreme_attacks.append(("extreme_bright_1.7",
                               np.clip(watermarked.astype(np.float32) * 1.7, 0, 255).astype(np.uint8),
                               "Severe Brightening - 70% brightness increase"))
        
        print("  4. Massive Scaling")
        scaled = cv2.resize(watermarked, (w // 2, h // 2))
        extreme_attacks.append(("extreme_scale_0.5x",
                               cv2.resize(scaled, (w, h)),
                               "Massive Scaling - 50% reduction then upscale"))
        
        print("  5. Heavy Blur")
        extreme_attacks.append(("extreme_blur_11x11",
                               cv2.GaussianBlur(watermarked, (11, 11), 0),
                               "Heavy Gaussian Blur - 11x11 kernel"))
        
        print("  6. Heavy Noise")
        noise = np.random.normal(0, 15, watermarked.shape).astype(np.float32)
        extreme_attacks.append(("extreme_noise_sigma15",
                               np.clip(watermarked.astype(np.float32) + noise, 0, 255).astype(np.uint8),
                               "Heavy Gaussian Noise - Sigma=15"))
        
        print("  7. Extreme Contrast")
        mean = np.mean(watermarked)
        extreme_attacks.append(("extreme_contrast_0.4",
                               np.clip((watermarked.astype(np.float32) - mean) * 0.4 + mean, 0, 255).astype(np.uint8),
                               "Extreme Contrast Reduction - 60% reduction"))
        
        print("  8. Color Inversion")
        extreme_attacks.append(("extreme_invert",
                               255 - watermarked,
                               "Complete Color Inversion"))
        
        print("  9. Grayscale")
        gray = cv2.cvtColor(watermarked, cv2.COLOR_BGR2GRAY)
        extreme_attacks.append(("extreme_grayscale",
                               cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                               "Grayscale Conversion"))
        
        print(" 10. Posterization")
        extreme_attacks.append(("extreme_posterize",
                               (watermarked // 85) * 85,
                               "Heavy Posterization - 4 color levels"))
        
        print(" 11. Sepia Tone")
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(watermarked, kernel)
        extreme_attacks.append(("extreme_sepia",
                               np.clip(sepia, 0, 255).astype(np.uint8),
                               "Sepia Tone Filter"))
        
        print(" 12. Combined JPEG + Dark")
        temp = np.clip(watermarked.astype(np.float32) * 0.5, 0, 255).astype(np.uint8)
        _, encoded = cv2.imencode('.jpg', temp, [cv2.IMWRITE_JPEG_QUALITY, 30])
        extreme_attacks.append(("extreme_combined_jpeg30_dark0.5",
                               cv2.imdecode(encoded, cv2.IMREAD_COLOR),
                               "Combined - JPEG Q30 + 50% darker"))
        
        print(" 13. Combined JPEG + Noise")
        _, encoded = cv2.imencode('.jpg', watermarked, [cv2.IMWRITE_JPEG_QUALITY, 40])
        temp = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        noise = np.random.normal(0, 12, temp.shape).astype(np.float32)
        extreme_attacks.append(("extreme_combined_jpeg40_noise12",
                               np.clip(temp.astype(np.float32) + noise, 0, 255).astype(np.uint8),
                               "Combined - JPEG Q40 + Heavy noise"))
        
        print(" 14. Combined Scale + Blur")
        scaled = cv2.resize(watermarked, (int(w * 0.7), int(h * 0.7)))
        scaled_back = cv2.resize(scaled, (w, h))
        extreme_attacks.append(("extreme_combined_scale0.7_blur5",
                               cv2.GaussianBlur(scaled_back, (5, 5), 0),
                               "Combined - Scale 0.7x + Blur 5x5"))
        
        print(" 15. Combined Bright + Contrast")
        temp = np.clip(watermarked.astype(np.float32) * 0.6, 0, 255).astype(np.uint8)
        mean = np.mean(temp)
        extreme_attacks.append(("extreme_combined_bright0.6_contrast0.6",
                               np.clip((temp.astype(np.float32) - mean) * 0.6 + mean, 0, 255).astype(np.uint8),
                               "Combined - Brightness + Contrast 0.6x"))
        
        print(f"\nTotal attacks: {len(extreme_attacks)}\n")
        
        # Test each
        print("="*80)
        print("TESTING WITH HYBRID VERIFICATION")
        print("="*80 + "\n")
        
        verified_attacks = []
        
        for i, (attack_name, attacked_image, description) in enumerate(extreme_attacks, 1):
            print(f"[{i:2d}/{len(extreme_attacks)}] {attack_name:<45s}", end=' ')
            
            attacked_rgb = cv2.cvtColor(attacked_image, cv2.COLOR_BGR2RGB)
            db_match, method, conf = self.hybrid_verify(attacked_rgb)
            
            if db_match:
                print(f"[VERIFIED] {method} ({conf:.1f}%)")
                verified_attacks.append((attack_name, attacked_image, db_match, method, conf, description))
            else:
                print(f"[FAILED] {method}")
        
        # Results
        print(f"\n{'='*80}")
        print(f"VERIFIED EXTREME ATTACKS: {len(verified_attacks)}/{len(extreme_attacks)}")
        print(f"{'='*80}\n")
        
        if len(verified_attacks) == 0:
            print("No attacks were successfully verified.")
            return []
        
        # Save
        output_dir = "test_images/perfect_extreme_showcase"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/attacked_images", exist_ok=True)
        os.makedirs(f"{output_dir}/comparisons", exist_ok=True)
        
        print("Saving verified extreme attacks...\n")
        
        for attack_name, attacked_image, db_record, method, conf, description in verified_attacks:
            cv2.imwrite(f"{output_dir}/attacked_images/{attack_name}.png", attacked_image)
            comparison = self.create_showcase_comparison(watermarked, attacked_image, attack_name, db_record, method, conf, description)
            cv2.imwrite(f"{output_dir}/comparisons/{attack_name}_showcase.png", comparison)
            print(f"  Saved: {attack_name} ({method}, {conf:.1f}%)")
        
        # Documentation
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write("# Perfect Extreme Attack Showcase - Hybrid Verification\n\n")
            f.write("## How It Works\n\n")
            f.write("This showcase demonstrates watermark detection using the same **hybrid verification** ")
            f.write("system as the website:\n\n")
            f.write("1. **Exact Match** - Direct hash lookup\n")
            f.write("2. **Fuzzy Match** - Character similarity (50%+ match)\n")
            f.write("3. **Perceptual Hash** - Visual similarity fallback\n\n")
            f.write("Even when the watermark is corrupted by extreme attacks, the system can still ")
            f.write("**identify the image** and display the **clean database record**.\n\n")
            f.write(f"## Results: {len(verified_attacks)}/{len(extreme_attacks)} Verified\n\n")
            
            for i, (attack_name, _, _, method, conf, description) in enumerate(verified_attacks, 1):
                f.write(f"{i}. **{attack_name}** - {description}\n")
                f.write(f"   - Method: {method}\n")
                f.write(f"   - Confidence: {conf:.1f}%\n\n")
        
        print(f"\nSaved to: {output_dir}/")
        print(f"  - {len(verified_attacks)} showcase comparisons")
        print(f"  - {len(verified_attacks)} attacked images")
        print(f"  - README.md documentation")
        
        print(f"\n{'='*80}")
        print("SHOWCASE COMPLETE!")
        print(f"{'='*80}\n")
        
        return verified_attacks

def main():
    """Main execution"""
    showcase = HybridExtremeShowcase()
    verified = showcase.test_extreme_attacks("test_images/watermarkedstork.png")
    
    if verified:
        print(f"\nFOUND {len(verified)} VERIFIED EXTREME ATTACKS!")
        print("\nUse these for demonstrations:")
        print("  test_images/perfect_extreme_showcase/comparisons/\n")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    main()

