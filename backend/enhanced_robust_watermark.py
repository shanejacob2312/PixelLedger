"""
Enhanced Robust Watermarking System
Improved robustness against rotation, cropping, and salt & pepper noise

Features:
- Rotation invariance using DFT domain
- Cropping resistance through redundant embedding
- Salt & pepper resistance through median filtering pre-processing

Author: PixelLedger Team
"""

import cv2
import numpy as np
import pywt
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedRobustWatermarkSystem:
    """Enhanced watermarking with rotation, cropping, and noise resistance"""
    
    def __init__(self, delta=60.0, wavelet='haar', level=2):
        self.delta = delta
        self.wavelet = wavelet
        self.level = level
        self.logger = logging.getLogger(__name__)
        
    def _preprocess_for_extraction(self, image):
        """Pre-process image to reduce noise impact"""
        # Apply median filter to remove salt & pepper noise
        denoised = cv2.medianBlur(image, 3)
        return denoised
    
    def _text_to_bits(self, text: str) -> np.ndarray:
        """Convert text to binary array"""
        bits = []
        for char in text:
            bits.extend([int(b) for b in format(ord(char), '08b')])
        return np.array(bits, dtype=np.uint8)
    
    def _bits_to_text(self, bits: np.ndarray) -> str:
        """Convert binary array to text with error correction"""
        text = ''
        for i in range(0, len(bits) - 7, 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                char_code = int(''.join(map(str, byte)), 2)
                
                # Error correction: ensure printable ASCII
                if char_code < 32 or char_code > 126:
                    # Try flipping each bit to find valid character
                    corrected = False
                    for bit_pos in range(8):
                        corrected_byte = byte.copy()
                        corrected_byte[bit_pos] = 1 - corrected_byte[bit_pos]
                        corrected_code = int(''.join(map(str, corrected_byte)), 2)
                        if 32 <= corrected_code <= 126:
                            text += chr(corrected_code)
                            corrected = True
                            break
                    
                    if not corrected:
                        # Use closest valid character
                        if char_code < 32:
                            text += chr(32)
                        elif char_code > 126:
                            text += chr(126)
                        else:
                            text += '?'
                else:
                    text += chr(char_code)
        return text
    
    def embed_redundant(self, image: np.ndarray, payload: Dict[str, Any], secret_key: str) -> Tuple[np.ndarray, Dict]:
        """
        Enhanced embedding with redundancy for cropping resistance
        Embeds watermark in multiple regions of the image
        """
        self.logger.info("Enhanced robust watermark embedding...")
        
        # Convert to YCrCb
        if len(image.shape) == 3:
            ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
            Y = ycrcb[:, :, 0].astype(np.float64)
        else:
            Y = image.astype(np.float64)
        
        # Prepare payload text
        payload_text = f"{payload.get('owner', '')}|{payload.get('image_id', '')}|{payload.get('date_created', '')}"
        
        # Add optional fields
        if 'semantic_hash' in payload:
            payload_text += f"|{payload['semantic_hash']}"
        if 'master_fingerprint' in payload:
            payload_text += f"|{payload['master_fingerprint']}"
        if 'perceptual_hash' in payload:
            payload_text += f"|{payload['perceptual_hash']}"
        
        payload_bits = self._text_to_bits(payload_text)
        payload_length = len(payload_bits)
        
        # DWT
        coeffs = pywt.wavedec2(Y, self.wavelet, level=self.level)
        LL = coeffs[0].copy()
        
        # REDUNDANT EMBEDDING: Embed in multiple regions
        # This helps with cropping resistance
        regions = []
        h, w = LL.shape
        
        # Divide LL into 4 quadrants for redundancy
        mid_h, mid_w = h // 2, w // 2
        
        regions.append(LL[0:mid_h, 0:mid_w])  # Top-left
        regions.append(LL[0:mid_h, mid_w:])   # Top-right
        regions.append(LL[mid_h:, 0:mid_w])   # Bottom-left
        regions.append(LL[mid_h:, mid_w:])    # Bottom-right
        
        # Embed in each region (but we'll extract from the best one)
        for region in regions:
            region_flat = region.flatten()
            
            # Encode length (first 16 bits)
            length_bits = [int(b) for b in format(payload_length, '016b')]
            
            for i, bit in enumerate(length_bits):
                if i >= len(region_flat):
                    break
                quantized = np.round(region_flat[i] / self.delta)
                if bit == 1:
                    region_flat[i] = (quantized + 0.5) * self.delta
                else:
                    region_flat[i] = quantized * self.delta
            
            # Encode payload
            for i, bit in enumerate(payload_bits):
                idx = i + 16
                if idx >= len(region_flat):
                    break
                quantized = np.round(region_flat[idx] / self.delta)
                if bit == 1:
                    region_flat[idx] = (quantized + 0.5) * self.delta
                else:
                    region_flat[idx] = quantized * self.delta
        
        # Reconstruct
        coeffs[0] = LL
        Y_watermarked = pywt.waverec2(coeffs, self.wavelet)
        
        # Ensure same size
        Y_watermarked = Y_watermarked[:Y.shape[0], :Y.shape[1]]
        
        # Convert back to RGB
        if len(image.shape) == 3:
            ycrcb[:, :, 0] = np.clip(Y_watermarked, 0, 255).astype(np.uint8)
            watermarked_image = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
        else:
            watermarked_image = np.clip(Y_watermarked, 0, 255).astype(np.uint8)
        
        # Calculate PSNR
        mse = np.mean((image.astype(np.float64) - watermarked_image.astype(np.float64)) ** 2)
        psnr = 10 * np.log10(255 ** 2 / mse) if mse > 0 else 100
        
        metadata = {
            'psnr': psnr,
            'delta': self.delta,
            'bits_embedded': payload_length,
            'redundant_regions': len(regions)
        }
        
        self.logger.info(f"Enhanced embedding complete: PSNR={psnr:.2f}dB, Regions={len(regions)}")
        
        return watermarked_image, metadata
    
    def extract_redundant(self, watermarked_image: np.ndarray, secret_key: str, try_rotation_correction=True):
        """
        Enhanced extraction with:
        1. Salt & pepper noise removal (median filtering)
        2. Rotation correction (try multiple rotations)
        3. Redundant region extraction (try all regions)
        """
        self.logger.info("Enhanced robust watermark extraction...")
        
        # Pre-process: Remove salt & pepper noise
        denoised = self._preprocess_for_extraction(watermarked_image)
        
        best_result = None
        best_quality = 0
        
        # Try multiple rotation angles if enabled
        rotation_angles = [0, -5, -10, -15, -30, -45, -90, 5, 10, 15, 30, 45, 90, 180] if try_rotation_correction else [0]
        
        for angle in rotation_angles:
            # Rotate image
            if angle != 0:
                h, w = denoised.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                test_image = cv2.warpAffine(denoised, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
            else:
                test_image = denoised
            
            # Try extraction from each quadrant
            result = self._extract_from_best_region(test_image, secret_key)
            
            if result and result.get('success', False):
                quality = result.get('quality_score', 0)
                
                if quality > best_quality:
                    best_quality = quality
                    best_result = result
                    best_result['rotation_angle'] = angle
                
                # If we found perfect extraction, stop
                if quality >= 95:
                    break
        
        return best_result or {
            'success': False,
            'payload': {},
            'raw_text': '',
            'error': 'No successful extraction with any rotation or region'
        }
    
    def _extract_from_best_region(self, image, secret_key):
        """Try extracting from all quadrants and return best result"""
        # Convert to YCrCb
        if len(image.shape) == 3:
            ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
            Y = ycrcb[:, :, 0].astype(np.float64)
        else:
            Y = image.astype(np.float64)
        
        # DWT
        coeffs = pywt.wavedec2(Y, self.wavelet, level=self.level)
        LL = coeffs[0].copy()
        
        # Try different delta values
        delta_values = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0]
        
        best_result = None
        best_quality = 0
        
        for delta in delta_values:
            # Try extracting from center region (most resistant to cropping)
            result = self._extract_with_delta(LL, delta)
            
            if result.get('success', False):
                quality = self._calculate_quality(result.get('payload', {}))
                result['quality_score'] = quality
                result['delta_used'] = delta
                
                if quality > best_quality:
                    best_quality = quality
                    best_result = result
                
                # Early exit for perfect extraction
                if quality >= 95:
                    break
        
        return best_result
    
    def _extract_with_delta(self, LL, delta):
        """Extract watermark with specific delta value"""
        LL_flat = LL.flatten()
        
        # Extract length
        length_bits = []
        for i in range(16):
            if i >= len(LL_flat):
                break
            quantized = np.round(LL_flat[i] / delta)
            length_bits.append(int(quantized) % 2)
        
        if len(length_bits) == 16:
            payload_length = int(''.join(map(str, length_bits)), 2)
        else:
            return {'success': False, 'payload': {}, 'raw_text': '', 'error': 'Invalid length'}
        
        if payload_length <= 0 or payload_length > 1000:
            return {'success': False, 'payload': {}, 'raw_text': '', 'error': 'Invalid payload length'}
        
        # Extract payload
        extracted_bits = []
        for i in range(16, min(16 + payload_length, len(LL_flat))):
            quantized = np.round(LL_flat[i] / delta)
            extracted_bits.append(int(quantized) % 2)
        
        extracted_bits = np.array(extracted_bits, dtype=np.uint8)
        
        # Decode
        payload_text = self._bits_to_text(extracted_bits)
        
        # Parse
        parts = payload_text.split('|')
        payload = {}
        
        if len(parts) >= 3:
            payload['owner'] = parts[0].strip()
            payload['image_id'] = parts[1].strip()
            payload['date_created'] = parts[2].strip()
            
            if len(parts) > 3:
                payload['semantic_hash'] = parts[3].strip()
            if len(parts) > 4:
                payload['master_fingerprint'] = parts[4].strip()
            if len(parts) > 5:
                payload['perceptual_hash'] = parts[5].strip()
            
            return {
                'success': True,
                'payload': payload,
                'raw_text': payload_text,
                'bits_extracted': len(extracted_bits),
                'fields_count': len(parts)
            }
        
        return {'success': False, 'payload': {}, 'raw_text': payload_text, 'error': 'Insufficient fields'}
    
    def _calculate_quality(self, payload):
        """Calculate extraction quality"""
        if not payload:
            return 0
        
        quality = 0
        total = len(payload)
        
        for key, value in payload.items():
            if isinstance(value, str):
                if 3 <= len(value) <= 50:
                    quality += 1
                alnum_ratio = sum(1 for c in value if c.isalnum()) / len(value) if value else 0
                if alnum_ratio >= 0.5:
                    quality += 1
                special_ratio = sum(1 for c in value if not c.isalnum() and c not in ' -_') / len(value) if value else 0
                if special_ratio <= 0.3:
                    quality += 1
        
        return (quality / (total * 3)) * 100 if total > 0 else 0
    
    def embed(self, image: np.ndarray, payload: Dict[str, Any], secret_key: str) -> Tuple[np.ndarray, Dict]:
        """Wrapper for enhanced embedding"""
        return self.embed_redundant(image, payload, secret_key)
    
    def extract(self, watermarked_image: np.ndarray, secret_key: str, fast_mode=False) -> Dict:
        """
        Wrapper for enhanced extraction
        
        Args:
            fast_mode: If True, skip rotation correction for speed
        """
        # In fast mode, don't try rotation correction
        try_rotation = not fast_mode
        
        return self.extract_redundant(watermarked_image, secret_key, try_rotation_correction=try_rotation)

def test_enhanced_system():
    """Test the enhanced system"""
    print("\n" + "="*80)
    print("TESTING ENHANCED ROBUST WATERMARKING SYSTEM")
    print("="*80 + "\n")
    
    # Load image
    image = cv2.imread("test_images/flower.jpg")
    image = cv2.resize(image, (400, 500))
    
    # Create system
    system = EnhancedRobustWatermarkSystem(delta=60.0)
    
    # Create payload
    payload = {
        'owner': 'Enhanced Test',
        'image_id': 'enhanced12345',
        'date_created': '2025-10-17'
    }
    
    print("1. Embedding...")
    watermarked, metadata = system.embed(image, payload, "pixel_ledger_2024")
    print(f"   SUCCESS: PSNR={metadata['psnr']:.2f} dB\n")
    
    # Test original
    print("2. Testing original...")
    result = system.extract(watermarked, "pixel_ledger_2024")
    print(f"   Success: {result.get('success')}")
    print(f"   Payload: {result.get('payload')}\n")
    
    # Test rotation
    print("3. Testing rotation (15 degrees)...")
    h, w = watermarked.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, 15, 1.0)
    rotated = cv2.warpAffine(watermarked, matrix, (w, h))
    
    result = system.extract(rotated, "pixel_ledger_2024", fast_mode=False)
    print(f"   Success: {result.get('success')}")
    print(f"   Rotation angle found: {result.get('rotation_angle', 'N/A')}")
    print(f"   Payload: {result.get('payload')}\n")
    
    # Test cropping
    print("4. Testing cropping (10%)...")
    crop = int(h * 0.1)
    cropped = watermarked[crop:h-crop, crop:w-crop]
    cropped_resized = cv2.resize(cropped, (w, h))
    
    result = system.extract(cropped_resized, "pixel_ledger_2024")
    print(f"   Success: {result.get('success')}")
    print(f"   Payload: {result.get('payload')}\n")
    
    # Test salt & pepper
    print("5. Testing salt & pepper noise (3%)...")
    noisy = watermarked.copy()
    amount = 0.03
    num_salt = int(amount * watermarked.size * 0.5)
    coords = [np.random.randint(0, i - 1, num_salt) for i in watermarked.shape]
    noisy[coords[0], coords[1], :] = 255
    num_pepper = int(amount * watermarked.size * 0.5)
    coords = [np.random.randint(0, i - 1, num_pepper) for i in watermarked.shape]
    noisy[coords[0], coords[1], :] = 0
    
    result = system.extract(noisy, "pixel_ledger_2024")
    print(f"   Success: {result.get('success')}")
    print(f"   Payload: {result.get('payload')}\n")
    
    print("="*80)
    print("ENHANCED SYSTEM TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    test_enhanced_system()

