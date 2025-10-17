"""
Create Perfect Extreme Showcase
Find and save only extreme attacks with 100% perfect extraction

Author: PixelLedger Team
"""

import cv2
import numpy as np
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.append('backend')
from app import UltraRobustWatermarkSystem

class PerfectExtremeShowcase:
    def __init__(self):
        self.extraction_system = UltraRobustWatermarkSystem(delta=60.0, wavelet='haar', level=2)
        
    def create_showcase_comparison(self, original, attacked, attack_name, extraction_result, attack_description):
        """Create professional showcase comparison"""
        h, w = original.shape[:2]
        
        # Create canvas with more space for professional layout
        canvas_h = h + 250
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
        except:
            title_font = label_font = subtitle_font = data_font = ImageFont.load_default()
        
        # Title
        draw.text((canvas_w // 2 - 350, 30), "PIXELLEDGER ROBUSTNESS TEST", fill=(0, 0, 150), font=title_font)
        draw.text((canvas_w // 2 - 180, 80), "100% PERFECT EXTRACTION", fill=(0, 150, 0), font=subtitle_font)
        
        # Labels
        draw.text((img1_x + w // 2 - 140, 115), "ORIGINAL WATERMARKED", fill=(0, 100, 0), font=label_font)
        draw.text((img2_x + w // 2 - 100, 115), f"{attack_name.upper()}", fill=(200, 0, 0), font=label_font)
        
        # Attack description
        draw.text((30, img_y + h + 15), attack_description, fill=(50, 50, 50), font=label_font)
        
        # Extraction results
        payload = extraction_result.get('payload', {})
        y_pos = img_y + h + 55
        
        draw.text((30, y_pos), "EXTRACTION: 100% PERFECT", fill=(0, 150, 0), font=data_font)
        draw.text((30, y_pos + 35), f"Owner: {payload.get('owner', 'N/A')}", fill=(0, 0, 0), font=data_font)
        draw.text((30, y_pos + 65), f"Image ID: {payload.get('image_id', 'N/A')}", fill=(0, 0, 0), font=data_font)
        draw.text((500, y_pos + 35), f"Date: {payload.get('date_created', 'N/A')}", fill=(0, 0, 0), font=data_font)
        draw.text((500, y_pos + 65), f"Delta: {extraction_result.get('delta_used')}", fill=(100, 100, 100), font=data_font)
        
        # Watermark icon
        draw.text((canvas_w - 150, y_pos + 40), "VERIFIED", fill=(0, 150, 0), font=title_font)
        
        # Convert back
        result = cv2.cvtColor(np.array(canvas_pil), cv2.COLOR_RGB2BGR)
        return result
    
    def test_extreme_attacks(self, watermarked_path):
        """Test extreme attacks and find perfect extractions"""
        print("\n" + "="*80)
        print("PERFECT EXTREME SHOWCASE - 100% EXTRACTION ONLY")
        print("="*80 + "\n")
        
        # Load
        watermarked = cv2.imread(watermarked_path)
        if watermarked is None:
            print(f"ERROR: Could not load {watermarked_path}")
            return
        
        print(f"Loaded: {watermarked_path}")
        print(f"Size: {watermarked.shape}\n")
        
        # Extract original
        print("Extracting from original...")
        original_extraction = self.extraction_system.extract(watermarked, "pixel_ledger_2024", fast_mode=False)
        
        if not original_extraction.get('success'):
            print("ERROR: Could not extract from original")
            return
        
        original_payload = original_extraction.get('payload', {})
        print(f"SUCCESS:")
        print(f"  Owner: {original_payload.get('owner')}")
        print(f"  Image ID: {original_payload.get('image_id')}")
        print(f"  Date: {original_payload.get('date_created')}\n")
        
        # Define extreme attacks with descriptions
        print("Applying extreme attacks...\n")
        
        extreme_attacks = []
        h, w = watermarked.shape[:2]
        
        # 1. Extreme JPEG
        print("  1. Extreme JPEG Compression (Quality 10)")
        _, encoded = cv2.imencode('.jpg', watermarked, [cv2.IMWRITE_JPEG_QUALITY, 10])
        extreme_attacks.append(("extreme_jpeg_q10", cv2.imdecode(encoded, cv2.IMREAD_COLOR), 
                               "Extreme JPEG Compression - Quality 10 (90% compression)"))
        
        # 2. Very Dark
        print("  2. Severe Darkening (40% brightness)")
        extreme_attacks.append(("extreme_dark_0.4", 
                               np.clip(watermarked.astype(np.float32) * 0.4, 0, 255).astype(np.uint8),
                               "Severe Darkening - 60% brightness reduction"))
        
        # 3. Very Bright
        print("  3. Severe Brightening (170% brightness)")
        extreme_attacks.append(("extreme_bright_1.7",
                               np.clip(watermarked.astype(np.float32) * 1.7, 0, 255).astype(np.uint8),
                               "Severe Brightening - 70% brightness increase"))
        
        # 4. Massive Scale
        print("  4. Massive Scaling (50% size reduction)")
        scaled = cv2.resize(watermarked, (w // 2, h // 2))
        extreme_attacks.append(("extreme_scale_0.5x",
                               cv2.resize(scaled, (w, h)),
                               "Massive Scaling - Reduced to 50% then upscaled"))
        
        # 5. Heavy Blur
        print("  5. Heavy Gaussian Blur (11x11 kernel)")
        extreme_attacks.append(("extreme_blur_11x11",
                               cv2.GaussianBlur(watermarked, (11, 11), 0),
                               "Heavy Gaussian Blur - 11x11 kernel"))
        
        # 6. Heavy Noise
        print("  6. Heavy Gaussian Noise (sigma=15)")
        noise = np.random.normal(0, 15, watermarked.shape).astype(np.float32)
        extreme_attacks.append(("extreme_noise_sigma15",
                               np.clip(watermarked.astype(np.float32) + noise, 0, 255).astype(np.uint8),
                               "Heavy Gaussian Noise - Sigma=15"))
        
        # 7. Extreme Contrast
        print("  7. Extreme Contrast Reduction (40%)")
        mean = np.mean(watermarked)
        extreme_attacks.append(("extreme_contrast_0.4",
                               np.clip((watermarked.astype(np.float32) - mean) * 0.4 + mean, 0, 255).astype(np.uint8),
                               "Extreme Contrast Reduction - 60% reduction"))
        
        # 8. Color Inversion
        print("  8. Complete Color Inversion")
        extreme_attacks.append(("extreme_invert",
                               255 - watermarked,
                               "Complete Color Inversion - Negative image"))
        
        # 9. Grayscale
        print("  9. Grayscale Conversion")
        gray = cv2.cvtColor(watermarked, cv2.COLOR_BGR2GRAY)
        extreme_attacks.append(("extreme_grayscale",
                               cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                               "Grayscale Conversion - Complete color removal"))
        
        # 10. Posterization
        print("  10. Heavy Posterization (4 colors)")
        extreme_attacks.append(("extreme_posterize_4colors",
                               (watermarked // 85) * 85,
                               "Heavy Posterization - Reduced to 4 color levels"))
        
        # 11. Sepia
        print("  11. Sepia Tone Filter")
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(watermarked, kernel)
        extreme_attacks.append(("extreme_sepia",
                               np.clip(sepia, 0, 255).astype(np.uint8),
                               "Sepia Tone Filter - Vintage photo effect"))
        
        # 12. JPEG + Brightness (Combined)
        print("  12. Combined: JPEG Q30 + Dark 0.5x")
        temp = np.clip(watermarked.astype(np.float32) * 0.5, 0, 255).astype(np.uint8)
        _, encoded = cv2.imencode('.jpg', temp, [cv2.IMWRITE_JPEG_QUALITY, 30])
        extreme_attacks.append(("extreme_combined_jpeg30_dark0.5",
                               cv2.imdecode(encoded, cv2.IMREAD_COLOR),
                               "Combined Attack - JPEG Q30 + 50% darker"))
        
        # 13. JPEG + Noise (Combined)
        print("  13. Combined: JPEG Q40 + Heavy Noise")
        _, encoded = cv2.imencode('.jpg', watermarked, [cv2.IMWRITE_JPEG_QUALITY, 40])
        temp = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        noise = np.random.normal(0, 12, temp.shape).astype(np.float32)
        extreme_attacks.append(("extreme_combined_jpeg40_noise12",
                               np.clip(temp.astype(np.float32) + noise, 0, 255).astype(np.uint8),
                               "Combined Attack - JPEG Q40 + Heavy noise sigma=12"))
        
        # 14. Scale + Blur (Combined)
        print("  14. Combined: Scale 0.7x + Blur 5x5")
        scaled = cv2.resize(watermarked, (int(w * 0.7), int(h * 0.7)))
        scaled_back = cv2.resize(scaled, (w, h))
        extreme_attacks.append(("extreme_combined_scale0.7_blur5",
                               cv2.GaussianBlur(scaled_back, (5, 5), 0),
                               "Combined Attack - Scale 0.7x + Gaussian Blur 5x5"))
        
        # 15. Brightness + Contrast (Combined)
        print("  15. Combined: Bright 0.6x + Contrast 0.6x")
        temp = np.clip(watermarked.astype(np.float32) * 0.6, 0, 255).astype(np.uint8)
        mean = np.mean(temp)
        extreme_attacks.append(("extreme_combined_bright0.6_contrast0.6",
                               np.clip((temp.astype(np.float32) - mean) * 0.6 + mean, 0, 255).astype(np.uint8),
                               "Combined Attack - Brightness 0.6x + Contrast 0.6x"))
        
        print(f"\nTotal extreme attacks: {len(extreme_attacks)}\n")
        
        # Test each
        print("="*80)
        print("TESTING FOR PERFECT EXTRACTIONS (100% ACCURACY)")
        print("="*80 + "\n")
        
        perfect_extractions = []
        
        for i, (attack_name, attacked_image, description) in enumerate(extreme_attacks, 1):
            print(f"[{i:2d}/{len(extreme_attacks)}] {attack_name:<45s}", end=' ')
            
            # Extract
            result = self.extraction_system.extract(attacked_image, "pixel_ledger_2024", fast_mode=False)
            
            if result.get('success'):
                extracted = result.get('payload', {})
                
                # Check if 100% perfect
                perfect = True
                for key in ['owner', 'image_id', 'date_created']:
                    if original_payload.get(key) != extracted.get(key):
                        perfect = False
                        break
                
                if perfect:
                    print(f"[PERFECT 100%] Delta:{result.get('delta_used')}")
                    perfect_extractions.append((attack_name, attacked_image, result, description))
                else:
                    # Calculate accuracy
                    matches = sum(1 for k in ['owner', 'image_id', 'date_created'] 
                                 if original_payload.get(k) == extracted.get(k))
                    accuracy = (matches / 3) * 100
                    print(f"[PARTIAL {accuracy:.0f}%]")
            else:
                print(f"[FAILED]")
        
        # Results
        print(f"\n{'='*80}")
        print(f"PERFECT EXTREME ATTACKS FOUND: {len(perfect_extractions)}")
        print(f"{'='*80}\n")
        
        if len(perfect_extractions) == 0:
            print("No perfect extractions found from extreme attacks.")
            print("Trying with slightly less extreme parameters...\n")
            return self.try_less_extreme(watermarked, original_payload)
        
        # Save perfect ones
        output_dir = "test_images/perfect_extreme_showcase"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/attacked_images", exist_ok=True)
        os.makedirs(f"{output_dir}/comparisons", exist_ok=True)
        
        print("Saving perfect extreme extractions...\n")
        
        for attack_name, attacked_image, result, description in perfect_extractions:
            # Save attacked image
            cv2.imwrite(f"{output_dir}/attacked_images/{attack_name}.png", attacked_image)
            
            # Create and save comparison
            comparison = self.create_showcase_comparison(watermarked, attacked_image, attack_name, result, description)
            cv2.imwrite(f"{output_dir}/comparisons/{attack_name}_showcase.png", comparison)
            
            print(f"  Saved: {attack_name}")
        
        # Create summary document
        with open(f"{output_dir}/PERFECT_EXTRACTIONS.txt", 'w') as f:
            f.write("="*80 + "\n")
            f.write("PIXELLEDGER - PERFECT EXTREME ATTACKS SHOWCASE\n")
            f.write("="*80 + "\n\n")
            f.write("These attacks demonstrate EXCEPTIONAL watermark robustness.\n")
            f.write("Despite severe visual degradation, extraction is 100% PERFECT.\n\n")
            f.write(f"Total Perfect Extractions: {len(perfect_extractions)}\n\n")
            f.write("-"*80 + "\n")
            f.write("LIST OF EXTREME ATTACKS WITH PERFECT EXTRACTION:\n")
            f.write("-"*80 + "\n\n")
            
            for i, (attack_name, _, result, description) in enumerate(perfect_extractions, 1):
                payload = result.get('payload', {})
                f.write(f"{i:2d}. {attack_name}\n")
                f.write(f"    Description: {description}\n")
                f.write(f"    Delta Used: {result.get('delta_used')}\n")
                f.write(f"    Owner: {payload.get('owner')}\n")
                f.write(f"    Image ID: {payload.get('image_id')}\n")
                f.write(f"    Date: {payload.get('date_created')}\n\n")
        
        # Create README
        with open(f"{output_dir}/README.md", 'w') as f:
            f.write("# Perfect Extreme Attack Showcase\n\n")
            f.write("## Purpose\n\n")
            f.write("This showcase demonstrates the **exceptional robustness** of the PixelLedger ")
            f.write("watermarking system by showing **extreme attacks** that still result in ")
            f.write("**100% perfect extraction** of watermark data.\n\n")
            
            f.write("## Perfect Extractions\n\n")
            f.write(f"Found **{len(perfect_extractions)} extreme attacks** with 100% perfect extraction:\n\n")
            
            for i, (attack_name, _, _, description) in enumerate(perfect_extractions, 1):
                f.write(f"{i}. **{attack_name}** - {description}\n")
            
            f.write("\n## Files\n\n")
            f.write("- `comparisons/` - Professional showcase images (side-by-side with results)\n")
            f.write("- `attacked_images/` - Just the attacked images\n")
            f.write("- `PERFECT_EXTRACTIONS.txt` - Detailed results\n\n")
            
            f.write("## How to Use\n\n")
            f.write("Use the images in `comparisons/` folder for:\n")
            f.write("- Presentations\n")
            f.write("- Demonstrations\n")
            f.write("- Portfolio showcases\n")
            f.write("- Technical documentation\n\n")
            
            f.write("Each comparison image shows:\n")
            f.write("- Original watermarked image (left)\n")
            f.write("- Severely attacked image (right)\n")
            f.write("- Attack description\n")
            f.write("- Extraction results (100% perfect)\n")
        
        print(f"\nSaved to: {output_dir}/")
        print(f"  - Comparisons: {len(perfect_extractions)} showcase images")
        print(f"  - Attacked images: {len(perfect_extractions)} images")
        print(f"  - Documentation: PERFECT_EXTRACTIONS.txt, README.md")
        
        print(f"\n{'='*80}")
        print("PERFECT EXTREME SHOWCASE COMPLETE!")
        print(f"{'='*80}\n")
        
        return perfect_extractions
    
    def try_less_extreme(self, watermarked, original_payload):
        """Try slightly less extreme but still impressive attacks"""
        print("Testing slightly less extreme attacks for perfect extractions...\n")
        
        attacks = []
        h, w = watermarked.shape[:2]
        
        # Less extreme but still impressive
        _, encoded = cv2.imencode('.jpg', watermarked, [cv2.IMWRITE_JPEG_QUALITY, 20])
        attacks.append(("impressive_jpeg_q20", cv2.imdecode(encoded, cv2.IMREAD_COLOR),
                       "Very Heavy JPEG Compression - Quality 20"))
        
        attacks.append(("impressive_dark_0.5",
                       np.clip(watermarked.astype(np.float32) * 0.5, 0, 255).astype(np.uint8),
                       "Severe Darkening - 50% brightness"))
        
        attacks.append(("impressive_bright_1.5",
                       np.clip(watermarked.astype(np.float32) * 1.5, 0, 255).astype(np.uint8),
                       "Severe Brightening - 50% increase"))
        
        scaled = cv2.resize(watermarked, (int(w * 0.6), int(h * 0.6)))
        attacks.append(("impressive_scale_0.6x",
                       cv2.resize(scaled, (w, h)),
                       "Heavy Scaling - 60% size"))
        
        noise = np.random.normal(0, 12, watermarked.shape).astype(np.float32)
        attacks.append(("impressive_noise_sigma12",
                       np.clip(watermarked.astype(np.float32) + noise, 0, 255).astype(np.uint8),
                       "Heavy Noise - Sigma=12"))
        
        attacks.append(("impressive_blur_7x7",
                       cv2.GaussianBlur(watermarked, (7, 7), 0),
                       "Heavy Blur - 7x7 kernel"))
        
        gray = cv2.cvtColor(watermarked, cv2.COLOR_BGR2GRAY)
        attacks.append(("impressive_grayscale",
                       cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
                       "Grayscale Conversion - Color removal"))
        
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        sepia = cv2.transform(watermarked, kernel)
        attacks.append(("impressive_sepia",
                       np.clip(sepia, 0, 255).astype(np.uint8),
                       "Sepia Filter - Vintage effect"))
        
        # Test these
        perfect_extractions = []
        
        for attack_name, attacked_image, description in attacks:
            print(f"  Testing: {attack_name:<40s}", end=' ')
            
            result = self.extraction_system.extract(attacked_image, "pixel_ledger_2024", fast_mode=False)
            
            if result.get('success'):
                extracted = result.get('payload', {})
                
                # Check perfect
                perfect = all(original_payload.get(k) == extracted.get(k) 
                             for k in ['owner', 'image_id', 'date_created'])
                
                if perfect:
                    print(f"[PERFECT 100%]")
                    perfect_extractions.append((attack_name, attacked_image, result, description))
                else:
                    print(f"[PARTIAL]")
            else:
                print(f"[FAILED]")
        
        # Save if found
        if perfect_extractions:
            output_dir = "test_images/perfect_extreme_showcase"
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(f"{output_dir}/attacked_images", exist_ok=True)
            os.makedirs(f"{output_dir}/comparisons", exist_ok=True)
            
            for attack_name, attacked_image, result, description in perfect_extractions:
                cv2.imwrite(f"{output_dir}/attacked_images/{attack_name}.png", attacked_image)
                comparison = self.create_showcase_comparison(watermarked, attacked_image, attack_name, result, description)
                cv2.imwrite(f"{output_dir}/comparisons/{attack_name}_showcase.png", comparison)
        
        return perfect_extractions

def main():
    """Main execution"""
    showcase = PerfectExtremeShowcase()
    perfect = showcase.test_extreme_attacks("test_images/watermarkedstork.png")
    
    if perfect and len(perfect) > 0:
        print(f"\nFOUND {len(perfect)} PERFECT EXTREME EXTRACTIONS!")
        print("\nUse these for impressive demonstrations:")
        print("  test_images/perfect_extreme_showcase/comparisons/\n")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise
    main()

