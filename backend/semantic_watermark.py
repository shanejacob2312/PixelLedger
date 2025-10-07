#!/usr/bin/env python3
"""
Semantic Watermarking System with AI-Powered Features
Includes BLIP captioning, ResNet object detection, perceptual hashing, and blockchain fingerprinting
"""

import numpy as np
import cv2
import hashlib
import logging
from typing import Dict, Any, Tuple, List
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import imagehash
import json
from datetime import datetime

# Import the base watermark system
from watermark_final_working import FinalWatermarkSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticWatermarkSystem:
    """
    Advanced watermarking system with semantic context extraction.
    Combines traditional watermarking with AI-powered semantic analysis.
    """
    
    def __init__(self, delta: float = 40.0, wavelet: str = 'haar', level: int = 2):
        """Initialize semantic watermarking system."""
        # Base watermark system
        self.base_watermark = FinalWatermarkSystem(delta, wavelet, level)
        
        # Initialize models (lazy loading to save memory)
        self.blip_model = None
        self.blip_processor = None
        self.resnet_model = None
        self.resnet_transform = None
        self.imagenet_classes = None
        
        logger.info("Semantic Watermark System initialized")
    
    def _load_blip_model(self):
        """Lazy load BLIP model for caption generation."""
        if self.blip_model is None:
            try:
                from transformers import BlipProcessor, BlipForConditionalGeneration
                logger.info("Loading BLIP model...")
                self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                logger.info("BLIP model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load BLIP model: {e}")
                logger.warning("Continuing without BLIP captioning")
    
    def _load_resnet_model(self):
        """Lazy load ResNet model for object detection."""
        if self.resnet_model is None:
            try:
                logger.info("Loading ResNet-50 model...")
                self.resnet_model = models.resnet50(pretrained=True)
                self.resnet_model.eval()
                
                # Standard ImageNet preprocessing
                self.resnet_transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ])
                
                # Load ImageNet class names
                self._load_imagenet_classes()
                logger.info("ResNet-50 model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load ResNet model: {e}")
                logger.warning("Continuing without ResNet classification")
    
    def _load_imagenet_classes(self):
        """Load ImageNet class names."""
        # Simplified version - you can expand this
        self.imagenet_classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
            "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
            "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        ]
    
    def generate_caption(self, image: np.ndarray) -> str:
        """
        Generate natural language caption using BLIP.
        
        Phase 1: BLIP Caption Generation
        - Input: RGB image
        - Processing: BLIP model analyzes visual content
        - Output: Natural language description
        """
        try:
            self._load_blip_model()
            if self.blip_model is None:
                return "Caption generation unavailable"
            
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
            else:
                pil_image = image
            
            # Generate caption
            inputs = self.blip_processor(pil_image, return_tensors="pt")
            out = self.blip_model.generate(**inputs, max_length=50)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            
            logger.info(f"Generated caption: {caption}")
            return caption
            
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            return "Caption generation failed"
    
    def detect_objects(self, image: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Detect objects using ResNet-50.
        
        Phase 1: ResNet Object Detection
        - Input: Preprocessed image (224×224, normalized)
        - Processing: ResNet-50 classifies into 1000 ImageNet categories
        - Output: Top-K object classes with confidence scores
        """
        try:
            self._load_resnet_model()
            if self.resnet_model is None:
                return [{"class": "unknown", "confidence": 0.0}]
            
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
            else:
                pil_image = image
            
            # Preprocess and classify
            input_tensor = self.resnet_transform(pil_image).unsqueeze(0)
            
            with torch.no_grad():
                output = self.resnet_model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
            # Get top-K predictions
            top_prob, top_idx = torch.topk(probabilities, top_k)
            
            results = []
            for i in range(top_k):
                idx = top_idx[i].item()
                prob = top_prob[i].item()
                class_name = self.imagenet_classes[idx % len(self.imagenet_classes)]
                results.append({
                    "class": class_name,
                    "confidence": round(prob * 100, 2)
                })
            
            logger.info(f"Detected objects: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return [{"class": "detection failed", "confidence": 0.0}]
    
    def create_semantic_hash(self, caption: str, objects: List[Dict[str, Any]]) -> str:
        """
        Create semantic hash for tamper detection.
        
        Phase 1: Semantic Hash Creation
        - Input: Caption + object list
        - Processing: SHA256 hash of combined semantic string
        - Output: 16-character hex hash
        """
        # Combine caption and objects into semantic string
        object_string = ", ".join([f"{obj['class']}({obj['confidence']}%)" for obj in objects])
        semantic_string = f"{caption} | Objects: {object_string}"
        
        # Create SHA256 hash
        hash_obj = hashlib.sha256(semantic_string.encode('utf-8'))
        semantic_hash = hash_obj.hexdigest()[:16]  # 16-character hex
        
        logger.info(f"Semantic hash created: {semantic_hash}")
        return semantic_hash
    
    def compute_perceptual_hash(self, image: np.ndarray) -> str:
        """
        Compute perceptual hash (pHash).
        
        Phase 2: Perceptual Hashing
        - Input: Image file
        - Processing: Perceptual hash algorithm (imagehash library)
        - Output: 64-bit hash string
        - Purpose: Visual fingerprint resistant to compression/resizing
        """
        try:
            # Convert numpy array to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
            else:
                pil_image = image
            
            # Compute pHash (8x8 DCT-based)
            phash = imagehash.phash(pil_image, hash_size=8)
            phash_str = str(phash)
            
            logger.info(f"Perceptual hash: {phash_str}")
            return phash_str
            
        except Exception as e:
            logger.error(f"Perceptual hash computation failed: {e}")
            return "0" * 16
    
    def create_multilayer_fingerprint(
        self,
        image: np.ndarray,
        metadata: Dict[str, Any],
        semantic_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Create multi-layer fingerprint.
        
        Phase 3: Fingerprint Creation
        - H(image): Hash of perceptual hash for visual integrity
        - H(metadata): Hash of user metadata for ownership verification
        - H(features): Hash of semantic context for content verification
        - H(fingerprint): Hash of entire structure for blockchain storage
        """
        # Layer 1: Visual integrity (perceptual hash)
        phash = self.compute_perceptual_hash(image)
        h_image = hashlib.sha256(phash.encode()).hexdigest()
        
        # Layer 2: Ownership verification (metadata)
        metadata_string = json.dumps(metadata, sort_keys=True)
        h_metadata = hashlib.sha256(metadata_string.encode()).hexdigest()
        
        # Layer 3: Content verification (semantic features)
        semantic_string = json.dumps(semantic_context, sort_keys=True)
        h_features = hashlib.sha256(semantic_string.encode()).hexdigest()
        
        # Layer 4: Complete fingerprint
        combined = f"{h_image}|{h_metadata}|{h_features}"
        h_fingerprint = hashlib.sha256(combined.encode()).hexdigest()
        
        fingerprint = {
            "h_image": h_image,
            "h_metadata": h_metadata,
            "h_features": h_features,
            "h_fingerprint": h_fingerprint,
            "phash": phash,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Multi-layer fingerprint created: {h_fingerprint[:16]}...")
        return fingerprint
    
    def prepare_blockchain_payload(
        self,
        fingerprint: Dict[str, str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare blockchain-ready payload.
        
        Phase 3: Blockchain Payload Preparation
        - Extract: Essential verification data
        - Structure: Blockchain-ready format
        - Purpose: On-chain storage without full fingerprint
        """
        blockchain_payload = {
            "fingerprint": fingerprint["h_fingerprint"],
            "visual_hash": fingerprint["h_image"],
            "owner": metadata.get("owner", ""),
            "image_id": metadata.get("image_id", ""),
            "timestamp": fingerprint["timestamp"],
            "version": "1.0"
        }
        
        logger.info(f"Blockchain payload prepared for image: {metadata.get('image_id', 'unknown')}")
        return blockchain_payload
    
    def embed(self, image: np.ndarray, payload: Dict[str, Any], secret_key: str) -> Tuple[np.ndarray, Dict]:
        """
        Enhanced embed with semantic context extraction.
        Embeds: owner|image_id|date|semantic_hash|fingerprint
        """
        logger.info("=== Starting Semantic Watermark Embedding ===")
        
        # Phase 1: Semantic Context Extraction
        logger.info("Phase 1: Extracting semantic context...")
        caption = self.generate_caption(image)
        objects = self.detect_objects(image, top_k=5)
        semantic_hash = self.create_semantic_hash(caption, objects)
        
        semantic_context = {
            "caption": caption,
            "objects": objects,
            "semantic_hash": semantic_hash
        }
        
        # Phase 2: Perceptual Hashing
        logger.info("Phase 2: Computing perceptual hash...")
        phash = self.compute_perceptual_hash(image)
        
        # Phase 3: Multi-layer Fingerprinting
        logger.info("Phase 3: Creating multi-layer fingerprint...")
        fingerprint = self.create_multilayer_fingerprint(image, payload, semantic_context)
        
        # Phase 4: Blockchain Payload
        logger.info("Phase 4: Preparing blockchain payload...")
        blockchain_payload = self.prepare_blockchain_payload(fingerprint, payload)
        
        # Phase 5: Enhanced Watermark Embedding
        # Add semantic hash and master fingerprint to embedded payload
        logger.info("Phase 5: Embedding enhanced watermark with semantic data...")
        
        # Use shorter hashes for more reliable embedding
        enhanced_payload = {
            **payload,
            'semantic_hash': semantic_hash[:16],  # 16 chars (already is)
            'master_fingerprint': fingerprint['h_fingerprint'][:16],  # Reduced to 16 chars for reliability
            'perceptual_hash': phash[:16]  # 16 chars
        }
        
        watermarked_image, base_metadata = self.base_watermark.embed(
            image, enhanced_payload, secret_key
        )
        
        # Combine all metadata
        enhanced_metadata = {
            **base_metadata,
            "semantic_context": semantic_context,
            "fingerprint": fingerprint,
            "blockchain_payload": blockchain_payload,
            "perceptual_hash": phash,
            "embedded_fields": [
                "owner", "image_id", "date_created", 
                "semantic_hash", "master_fingerprint", "perceptual_hash"
            ]
        }
        
        logger.info("=== Semantic Watermark Embedding Complete ===")
        logger.info(f"Embedded: owner, image_id, date, semantic_hash, fingerprint, phash")
        return watermarked_image, enhanced_metadata
    
    def extract(self, image: np.ndarray, secret_key: str) -> Dict[str, Any]:
        """Extract watermark using base system."""
        return self.base_watermark.extract(image, secret_key)
    
    def verify_integrity(
        self,
        image: np.ndarray,
        original_fingerprint: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Verify image integrity using fingerprints.
        """
        # Compute current perceptual hash
        current_phash = self.compute_perceptual_hash(image)
        
        # Compare with original
        original_phash = original_fingerprint.get("phash", "")
        
        # Calculate Hamming distance (for phash similarity)
        if original_phash and current_phash:
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(original_phash, current_phash))
            similarity = (1 - hamming_distance / len(original_phash)) * 100
        else:
            similarity = 0.0
        
        # Visual integrity check
        current_h_image = hashlib.sha256(current_phash.encode()).hexdigest()
        visual_match = current_h_image == original_fingerprint.get("h_image", "")
        
        verification = {
            "visual_integrity": visual_match,
            "perceptual_similarity": round(similarity, 2),
            "current_phash": current_phash,
            "original_phash": original_phash,
            "tampered": similarity < 90.0  # Threshold for tampering detection
        }
        
        logger.info(f"Integrity verification: similarity={similarity}%, tampered={verification['tampered']}")
        return verification

