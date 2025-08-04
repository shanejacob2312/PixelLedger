import numpy as np
import cv2
from typing import Optional, Dict, Any
import struct

class LSBWatermarker:
    def __init__(self, channel: int = 0):
        """
        Initialize LSB watermarker
        
        Args:
            channel: Color channel to use (0=Blue, 1=Green, 2=Red)
        """
        self.channel = channel

    def embed_watermark_lsb(self, image_path: str, watermark_data: bytes, output_path: str) -> bool:
        """
        Embed watermark data into image using LSB (Least Significant Bit) method
        
        Args:
            image_path: Path to input image
            watermark_data: Bytes to embed as watermark
            output_path: Path to save watermarked image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert watermark to binary array
            watermark_bits = self._bytes_to_bits(watermark_data)
            
            # Add length header and sync pattern
            length_bits = self._int_to_bits(len(watermark_data), 32)
            sync_pattern = [1, 0, 1, 0, 1, 0, 1, 0]  # 8-bit sync pattern
            all_bits = np.concatenate([sync_pattern, length_bits, watermark_bits])
            
            print(f"Debug: Embedding {len(all_bits)} bits")
            print(f"Debug: Sync pattern: {sync_pattern}")
            print(f"Debug: Length bits: {length_bits.tolist()}")
            print(f"Debug: First 20 bits: {all_bits[:20].tolist()}")
            
            # Check capacity
            height, width = image.shape[:2]
            available_bits = height * width
            if len(all_bits) > available_bits:
                raise ValueError(f"Watermark too large. Available: {available_bits} bits, needed: {len(all_bits)} bits")
            
            # Embed bits
            watermarked_image = self._embed_bits_lsb(image, all_bits)
            
            # Save watermarked image (use PNG to avoid compression artifacts)
            if not output_path.lower().endswith('.png'):
                output_path = output_path.replace('.jpg', '.png').replace('.jpeg', '.png')
            
            # Ensure PNG format for LSB preservation
            cv2.imwrite(output_path, watermarked_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            print(f"✅ Watermarked image saved as PNG: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error embedding watermark: {e}")
            return False

    def extract_watermark_lsb(self, image_path: str) -> Optional[bytes]:
        """
        Extract embedded watermark data from image using LSB method
        
        Args:
            image_path: Path to watermarked image
            
        Returns:
            bytes: Extracted watermark data or None if failed
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Extract bits
            extracted_bits = self._extract_bits_lsb(image)
            
            # Find sync pattern with multiple attempts
            sync_pattern = np.array([1, 0, 1, 0, 1, 0, 1, 0])
            sync_found = False
            start_index = 0
            
            print(f"Debug: Looking for sync pattern in {len(extracted_bits)} bits")
            print(f"Debug: First 20 bits: {extracted_bits[:20].tolist()}")
            
            # Try to find sync pattern in first 1000 bits (reasonable range)
            search_range = min(1000, len(extracted_bits) - 7)
            for i in range(search_range):
                if np.array_equal(extracted_bits[i:i+8], sync_pattern):
                    sync_found = True
                    start_index = i + 8
                    print(f"Debug: Sync pattern found at position {i}")
                    break
            
            if not sync_found:
                print("Warning: Sync pattern not found in first 1000 bits")
                print("This image may not be watermarked with LSB or may be corrupted")
                return None
            
            # Extract length
            if start_index + 32 >= len(extracted_bits):
                print("Warning: Not enough bits after sync pattern for length")
                return None
                
            length_bits = extracted_bits[start_index:start_index+32]
            data_length = self._bits_to_int(length_bits)
            
            print(f"Debug: Length bits: {length_bits.tolist()}")
            print(f"Debug: Data length: {data_length}")
            
            # More conservative validation - max 100KB instead of 1MB
            if data_length <= 0 or data_length > 100000:  # Max 100KB
                print(f"Warning: Invalid data length: {data_length} (max allowed: 100000)")
                print("This suggests the image may not be properly watermarked with LSB")
                return None
            
            # Check if we have enough bits for the data
            data_start = start_index + 32
            required_bits = data_length * 8
            available_bits = len(extracted_bits) - data_start
            
            if required_bits > available_bits:
                print(f"Warning: Not enough bits available. Required: {required_bits}, Available: {available_bits}")
                return None
            
            # Extract data
            data_bits = extracted_bits[data_start:data_start + required_bits]
            
            # Convert to bytes
            watermark_data = self._bits_to_bytes(data_bits)
            
            # Validate
            if len(watermark_data) != data_length:
                print(f"Warning: Expected {data_length} bytes, got {len(watermark_data)}")
                return None
            
            # Additional validation: try to decode as UTF-8 to check if it's valid data
            try:
                watermark_str = watermark_data.decode('utf-8')
                # Try to parse as JSON to validate structure
                import json
                json.loads(watermark_str)
                print("✅ Watermark data successfully extracted and validated")
                return watermark_data
            except UnicodeDecodeError:
                print("Warning: Extracted data is not valid UTF-8")
                return None
            except json.JSONDecodeError:
                print("Warning: Extracted data is not valid JSON")
                return None
            
        except Exception as e:
            print(f"Error extracting watermark: {e}")
            return None

    def _bytes_to_bits(self, data: bytes) -> np.ndarray:
        """Convert bytes to binary array"""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return np.array(bits, dtype=np.uint8)

    def _bits_to_bytes(self, bits: np.ndarray) -> bytes:
        """Convert binary array back to bytes"""
        # Ensure we have complete bytes
        num_bits = len(bits)
        num_bytes = num_bits // 8
        
        # If we don't have complete bytes, truncate to the nearest byte boundary
        if num_bits % 8 != 0:
            num_bits = num_bytes * 8
            bits = bits[:num_bits]
        
        result = bytearray()
        for i in range(num_bytes):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i * 8 + j]
            result.append(byte)
        
        return bytes(result)

    def _int_to_bits(self, value: int, num_bits: int) -> np.ndarray:
        """Convert integer to binary array"""
        bits = []
        for i in range(num_bits):
            bits.append((value >> (num_bits - 1 - i)) & 1)
        return np.array(bits, dtype=np.uint8)

    def _bits_to_int(self, bits: np.ndarray) -> int:
        """Convert binary array to integer"""
        value = 0
        for bit in bits:
            value = (value << 1) | int(bit)
        return value

    def _embed_bits_lsb(self, image: np.ndarray, bits: np.ndarray) -> np.ndarray:
        """Embed bits into LSB of image pixels"""
        watermarked_image = image.copy()
        height, width = image.shape[:2]
        
        bit_index = 0
        for i in range(height):
            for j in range(width):
                if bit_index >= len(bits):
                    break
                
                # Get pixel value
                pixel_value = watermarked_image[i, j, self.channel]
                
                # Clear LSB and set new bit
                pixel_value = (pixel_value & 0xFE) | int(bits[bit_index])
                
                # Update pixel
                watermarked_image[i, j, self.channel] = pixel_value
                
                bit_index += 1
        
        return watermarked_image

    def _extract_bits_lsb(self, image: np.ndarray) -> np.ndarray:
        """Extract bits from LSB of image pixels"""
        height, width = image.shape[:2]
        bits = []
        
        for i in range(height):
            for j in range(width):
                # Get pixel value
                pixel_value = image[i, j, self.channel]
                
                # Extract LSB
                bit = pixel_value & 1
                bits.append(bit)
        
        return np.array(bits, dtype=np.uint8)

    def estimate_capacity(self, image_path: str) -> int:
        """
        Estimate maximum watermark capacity for an image
        
        Args:
            image_path: Path to image
            
        Returns:
            int: Maximum number of bits that can be embedded
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0
            
            height, width = image.shape[:2]
            return height * width
            
        except Exception as e:
            print(f"Error estimating capacity: {e}")
            return 0

    def debug_extraction(self, image_path: str) -> Dict[str, Any]:
        """
        Debug watermark extraction process
        
        Args:
            image_path: Path to watermarked image
            
        Returns:
            Dict containing debug information
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": f"Could not read image: {image_path}"}
            
            # Extract bits
            extracted_bits = self._extract_bits_lsb(image)
            
            # Check for sync pattern
            sync_pattern = np.array([1, 0, 1, 0, 1, 0, 1, 0])
            sync_found = False
            sync_position = -1
            
            for i in range(len(extracted_bits) - 7):
                if np.array_equal(extracted_bits[i:i+8], sync_pattern):
                    sync_found = True
                    sync_position = i
                    break
            
            debug_info = {
                "total_bits_extracted": len(extracted_bits),
                "first_20_bits": extracted_bits[:20].tolist(),
                "sync_pattern_found": sync_found,
                "sync_position": sync_position,
                "extraction_success": sync_found
            }
            
            if sync_found:
                # Try to extract length and data
                length_bits = extracted_bits[sync_position+8:sync_position+40]
                data_length = self._bits_to_int(length_bits)
                debug_info["data_length"] = data_length
                
                # Try to extract data
                data_start = sync_position + 40
                data_bits = extracted_bits[data_start:data_start + data_length * 8]
                watermark_data = self._bits_to_bytes(data_bits)
                
                debug_info["total_bytes_extracted"] = len(watermark_data)
                debug_info["first_10_bytes_hex"] = watermark_data[:10].hex() if len(watermark_data) >= 10 else watermark_data.hex()
                
                # Try to decode as UTF-8
                try:
                    watermark_str = watermark_data.decode('utf-8')
                    debug_info["utf8_decode_success"] = True
                    debug_info["decoded_length"] = len(watermark_str)
                    debug_info["first_100_chars"] = watermark_str[:100]
                except UnicodeDecodeError as e:
                    debug_info["utf8_decode_success"] = False
                    debug_info["decode_error"] = str(e)
            
            return debug_info
            
        except Exception as e:
            return {"error": str(e)} 