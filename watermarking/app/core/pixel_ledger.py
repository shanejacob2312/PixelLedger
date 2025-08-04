import os
import json
from typing import Dict, Any, Optional, Tuple
from .semantic import SemanticExtractor
from .phash import compute_phash
from .fingerprint import SemanticFingerprint
from .lsb_watermark import LSBWatermarker

class PixelLedger:
    """
    Main orchestrator for PixelLedger semantic-aware digital watermarking system.
    
    Combines:
    - Semantic feature extraction (BLIP + ResNet)
    - Perceptual hashing
    - Self-verifiable fingerprint creation
    - LSB-based watermark embedding/extraction
    - Blockchain-ready payload generation
    """
    
    def __init__(self, watermark_strength: float = 20.0, use_lsb: bool = True):
        """
        Initialize PixelLedger system
        
        Args:
            watermark_strength: Watermark strength factor (for future use)
            use_lsb: Use LSB watermarking (always True now)
        """
        self.semantic_extractor = SemanticExtractor()
        self.fingerprint_creator = SemanticFingerprint()
        
        # Always use LSB watermarking
        self.watermarker = LSBWatermarker(channel=0)  # Use blue channel
        self.watermark_method = "LSB"
        print("✅ Using LSB watermarking (recommended for reliability)")
        
    def create_semantic_watermark(self, 
                                image_path: str, 
                                metadata: Dict[str, Any],
                                output_path: str) -> Dict[str, Any]:
        """
        Create and embed a semantic watermark into an image
        
        Args:
            image_path: Path to input image
            metadata: Dictionary containing author, description, etc.
            output_path: Path to save watermarked image
            
        Returns:
            Dict containing fingerprint and processing results
        """
        try:
            # Step 1: Extract semantic context
            print("Extracting semantic context...")
            semantic_context = self.semantic_extractor.extract_semantic_context(image_path)
            
            # Step 2: Compute perceptual hash
            print("Computing perceptual hash...")
            phash = compute_phash(image_path)
            
            # Step 3: Create self-verifiable fingerprint
            print("Creating semantic fingerprint...")
            fingerprint = self.fingerprint_creator.create_fingerprint(
                semantic_context=semantic_context,
                phash=phash,
                metadata=metadata
            )
            
            # Step 4: Serialize fingerprint for embedding
            fingerprint_bytes = self.fingerprint_creator.serialize_fingerprint(fingerprint).encode('utf-8')
            
            # Step 5: Check watermark capacity
            capacity = self.watermarker.estimate_capacity(image_path)
            if len(fingerprint_bytes) * 8 > capacity:
                raise ValueError(f"Fingerprint too large. Capacity: {capacity} bits, needed: {len(fingerprint_bytes) * 8} bits")
            
            # Step 6: Embed watermark
            print(f"Embedding semantic watermark using {self.watermark_method}...")
            success = self.watermarker.embed_watermark_lsb(
                image_path=image_path,
                watermark_data=fingerprint_bytes,
                output_path=output_path
            )
            
            if not success:
                raise RuntimeError("Failed to embed watermark")
            
            # Step 7: Prepare blockchain payload
            blockchain_payload = self.fingerprint_creator.get_blockchain_payload(fingerprint)
            
            return {
                "success": True,
                "fingerprint": fingerprint,
                "blockchain_payload": blockchain_payload,
                "semantic_context": semantic_context,
                "phash": phash,
                "watermarked_image_path": output_path,
                "capacity_used": len(fingerprint_bytes) * 8,
                "total_capacity": capacity
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_semantic_watermark(self, 
                                image_path: str,
                                blockchain_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify a semantic watermark from an image
        
        Args:
            image_path: Path to watermarked image
            blockchain_record: Optional blockchain record for verification
            
        Returns:
            Dict containing verification results
        """
        try:
            # Step 1: Extract watermark
            print(f"Extracting watermark using {self.watermark_method}...")
            watermark_bytes = self.watermarker.extract_watermark_lsb(image_path)
            
            if watermark_bytes is None:
                return {
                    "success": False,
                    "error": "No watermark found or extraction failed"
                }
            
            # Step 2: Deserialize fingerprint
            try:
                watermark_str = watermark_bytes.decode('utf-8')
                fingerprint = self.fingerprint_creator.deserialize_fingerprint(watermark_str)
            except UnicodeDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to decode watermark data as UTF-8: {e}. This may indicate watermark corruption or extraction issues."
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse watermark data as JSON: {e}. This may indicate watermark corruption or extraction issues."
                }
            
            # Step 3: Verify fingerprint integrity
            print("Verifying fingerprint integrity...")
            verification_results = self.fingerprint_creator.verify_fingerprint(fingerprint)
            
            # Step 4: Extract current semantic context for drift detection
            print("Extracting current semantic context...")
            current_semantic_context = self.semantic_extractor.extract_semantic_context(image_path)
            
            # Step 5: Detect semantic drift
            print("Detecting semantic drift...")
            drift_analysis = self.fingerprint_creator.detect_semantic_drift(
                original_fingerprint=fingerprint,
                current_semantic_context=current_semantic_context
            )
            
            # Step 6: Verify against blockchain (if provided)
            blockchain_verification = None
            if blockchain_record:
                blockchain_verification = {
                    "blockchain_hash_match": (
                        fingerprint["blockchain_hash"] == blockchain_record.get("blockchain_hash")
                    ),
                    "timestamp_match": (
                        fingerprint["timestamp"] == blockchain_record.get("timestamp")
                    )
                }
            
            return {
                "success": True,
                "fingerprint": fingerprint,
                "verification_results": verification_results,
                "drift_analysis": drift_analysis,
                "current_semantic_context": current_semantic_context,
                "blockchain_verification": blockchain_verification,
                "overall_authentic": (
                    verification_results["fingerprint_valid"] and 
                    not drift_analysis["drift_detected"] and
                    (blockchain_verification is None or blockchain_verification["blockchain_hash_match"])
                )
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and capabilities"""
        return {
            "system_name": "PixelLedger",
            "version": "1.0",
            "capabilities": [
                "Semantic context extraction (BLIP + ResNet)",
                "Perceptual hashing",
                "Self-verifiable fingerprinting",
                "LSB-based watermarking",
                "Semantic drift detection",
                "Blockchain-ready payloads"
            ],
            "watermark_method": "LSB",
            "channel": self.watermarker.channel
        } 