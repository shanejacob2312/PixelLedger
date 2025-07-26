import torch
from PIL import Image
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration
from torchvision import models, transforms
import torch.nn.functional as F

class SemanticExtractor:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # BLIP for captioning
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        
        # ResNet for object/scene classification
        self.resnet = models.resnet50(pretrained=True)
        self.resnet.eval()
        self.resnet.to(self.device)
        
        # ImageNet class labels (1000 classes)
        self.imagenet_labels = self._load_imagenet_labels()
        
        # Transform for ResNet
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_imagenet_labels(self):
        """Load ImageNet class labels"""
        # Simplified - in practice, you'd load the full ImageNet labels
        return [f"class_{i}" for i in range(1000)]

    def extract_caption(self, image_path: str) -> str:
        """Extract semantic caption using BLIP"""
        image = Image.open(image_path).convert("RGB")
        inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        out = self.blip_model.generate(**inputs)
        caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
        return caption

    def extract_object_features(self, image_path: str, top_k: int = 10) -> dict:
        """Extract top object/scene classifications using ResNet"""
        image = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.resnet(input_tensor)
            probabilities = F.softmax(output, dim=1)
            
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, top_k)
        
        features = {
            "objects": [],
            "confidence_scores": []
        }
        
        for i in range(top_k):
            label = self.imagenet_labels[top_indices[0][i].item()]
            confidence = top_probs[0][i].item()
            features["objects"].append(label)
            features["confidence_scores"].append(confidence)
            
        return features

    def extract_semantic_context(self, image_path: str) -> dict:
        """Extract comprehensive semantic context (caption + objects)"""
        caption = self.extract_caption(image_path)
        object_features = self.extract_object_features(image_path)
        
        return {
            "caption": caption,
            "detected_objects": object_features["objects"][:5],  # Top 5 objects
            "object_confidence": object_features["confidence_scores"][:5],
            "semantic_hash": self._hash_semantic_features(caption, object_features["objects"])
        }

    def _hash_semantic_features(self, caption: str, objects: list) -> str:
        """Create a hash of semantic features for tamper detection"""
        import hashlib
        semantic_string = f"{caption}:{':'.join(objects)}"
        return hashlib.sha256(semantic_string.encode()).hexdigest()[:16]  # 16 chars for compactness 