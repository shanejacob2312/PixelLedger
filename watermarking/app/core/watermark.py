import numpy as np
import cv2
from typing import Tuple, Optional
import struct

class DCTWatermarker:
    def __init__(self, block_size: int = 8, alpha: float = 20.0):
        """
        Initialize DCT watermarker
        
        Args:
            block_size: Size of DCT blocks (default: 8x8)
            alpha: Watermark strength factor (default: 20.0)
        """
        self.block_size = block_size
        self.alpha = alpha

    def embed_watermark_dct(self, image_path: str, watermark_data: bytes, output_path: str) -> bool:
        """
        Embed watermark data into image using DCT mid-frequency coefficients
        
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
            
            # Convert to YUV (watermark in Y channel)
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(np.float32)
            
            # Convert watermark to binary array
            watermark_bits = self._bytes_to_bits(watermark_data)
            
            # Embed watermark
            watermarked_y = self._embed_bits_in_dct(y_channel, watermark_bits)
            
            # Reconstruct image
            yuv[:, :, 0] = np.clip(watermarked_y, 0, 255).astype(np.uint8)
            watermarked_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
            
            # Save watermarked image
            cv2.imwrite(output_path, watermarked_image)
            return True
            
        except Exception as e:
            print(f"Error embedding watermark: {e}")
            return False

    def extract_watermark_dct(self, image_path: str) -> Optional[bytes]:
        """
        Extract embedded watermark data from image
        
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
            
            # Convert to YUV
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(np.float32)
            
            # Extract watermark bits
            watermark_bits = self._extract_bits_from_dct(y_channel)
            
            # Convert bits back to bytes
            watermark_data = self._bits_to_bytes(watermark_bits)
            
            return watermark_data
            
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
        
        result = bytearray()
        for i in range(num_bytes):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i * 8 + j]
            result.append(byte)
        
        return bytes(result)

    def _embed_bits_in_dct(self, image: np.ndarray, bits: np.ndarray) -> np.ndarray:
        """Embed bits into DCT mid-frequency coefficients"""
        height, width = image.shape
        embedded_image = image.copy()
        
        # Calculate number of blocks needed
        blocks_h = height // self.block_size
        blocks_w = width // self.block_size
        max_bits = blocks_h * blocks_w
        
        if len(bits) > max_bits:
            raise ValueError(f"Watermark too large. Max bits: {max_bits}, provided: {len(bits)}")
        
        bit_index = 0
        for i in range(blocks_h):
            for j in range(blocks_w):
                if bit_index >= len(bits):
                    break
                    
                # Extract block
                block = image[i * self.block_size:(i + 1) * self.block_size,
                             j * self.block_size:(j + 1) * self.block_size]
                
                # Apply DCT
                dct_block = cv2.dct(block.astype(np.float32))
                
                # Embed bit in mid-frequency coefficient (position 5,5)
                if bits[bit_index] == 1:
                    dct_block[5, 5] = abs(dct_block[5, 5]) + self.alpha
                else:
                    dct_block[5, 5] = abs(dct_block[5, 5]) - self.alpha
                
                # Apply inverse DCT
                idct_block = cv2.idct(dct_block)
                
                # Update embedded image
                embedded_image[i * self.block_size:(i + 1) * self.block_size,
                              j * self.block_size:(j + 1) * self.block_size] = idct_block
                
                bit_index += 1
        
        return embedded_image

    def _extract_bits_from_dct(self, image: np.ndarray) -> np.ndarray:
        """Extract bits from DCT mid-frequency coefficients"""
        height, width = image.shape
        blocks_h = height // self.block_size
        blocks_w = width // self.block_size
        
        bits = []
        for i in range(blocks_h):
            for j in range(blocks_w):
                # Extract block
                block = image[i * self.block_size:(i + 1) * self.block_size,
                             j * self.block_size:(j + 1) * self.block_size]
                
                # Apply DCT
                dct_block = cv2.dct(block.astype(np.float32))
                
                # Extract bit from mid-frequency coefficient
                coefficient = dct_block[5, 5]
                bit = 1 if coefficient > 0 else 0
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
            blocks_h = height // self.block_size
            blocks_w = width // self.block_size
            
            return blocks_h * blocks_w
            
        except Exception as e:
            print(f"Error estimating capacity: {e}")
            return 0 