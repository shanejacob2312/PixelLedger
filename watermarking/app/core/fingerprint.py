import json
import hashlib
from typing import Dict, Any
from datetime import datetime

class SemanticFingerprint:
    def __init__(self):
        pass

    def create_fingerprint(self, 
                          semantic_context: Dict[str, Any],
                          phash: str, 
                          metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a self-verifiable semantic fingerprint with multiple hash layers.
        
        Structure:
        - H(image): Hash of perceptual hash
        - H(metadata): Hash of metadata
        - H(features): Hash of semantic features
        - H(fingerprint): Hash of entire structure (for blockchain)
        """
        
        # Create individual hashes
        image_hash = self._hash_string(phash)
        metadata_hash = self._hash_dict(metadata)
        features_hash = self._hash_dict(semantic_context)
        
        # Create fingerprint structure
        fingerprint = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "hashes": {
                "image_hash": image_hash,
                "metadata_hash": metadata_hash,
                "features_hash": features_hash
            },
            "data": {
                "semantic_context": semantic_context,
                "phash": phash,
                "metadata": metadata
            }
        }
        
        # Create blockchain hash (hash of entire fingerprint)
        fingerprint_hash = self._hash_dict(fingerprint)
        fingerprint["blockchain_hash"] = fingerprint_hash
        
        return fingerprint

    def verify_fingerprint(self, fingerprint: Dict[str, Any]) -> Dict[str, bool]:
        """
        Verify the integrity of a fingerprint by recomputing hashes.
        Returns verification results for each component.
        """
        verification_results = {}
        
        # Verify image hash
        expected_image_hash = self._hash_string(fingerprint["data"]["phash"])
        verification_results["image_hash_valid"] = (
            fingerprint["hashes"]["image_hash"] == expected_image_hash
        )
        
        # Verify metadata hash
        expected_metadata_hash = self._hash_dict(fingerprint["data"]["metadata"])
        verification_results["metadata_hash_valid"] = (
            fingerprint["hashes"]["metadata_hash"] == expected_metadata_hash
        )
        
        # Verify features hash
        expected_features_hash = self._hash_dict(fingerprint["data"]["semantic_context"])
        verification_results["features_hash_valid"] = (
            fingerprint["hashes"]["features_hash"] == expected_features_hash
        )
        
        # Verify blockchain hash
        fingerprint_copy = fingerprint.copy()
        blockchain_hash = fingerprint_copy.pop("blockchain_hash")
        expected_blockchain_hash = self._hash_dict(fingerprint_copy)
        verification_results["blockchain_hash_valid"] = (
            blockchain_hash == expected_blockchain_hash
        )
        
        # Overall verification
        verification_results["fingerprint_valid"] = all(verification_results.values())
        
        return verification_results

    def detect_semantic_drift(self, original_fingerprint: Dict[str, Any], 
                            current_semantic_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect semantic drift by comparing original and current semantic contexts.
        """
        original_context = original_fingerprint["data"]["semantic_context"]
        
        drift_analysis = {
            "caption_changed": original_context["caption"] != current_semantic_context["caption"],
            "objects_changed": set(original_context["detected_objects"]) != set(current_semantic_context["detected_objects"]),
            "semantic_hash_changed": original_context["semantic_hash"] != current_semantic_context["semantic_hash"],
            "drift_detected": False
        }
        
        # Detect overall drift
        drift_analysis["drift_detected"] = (
            drift_analysis["caption_changed"] or 
            drift_analysis["objects_changed"] or 
            drift_analysis["semantic_hash_changed"]
        )
        
        return drift_analysis

    def serialize_fingerprint(self, fingerprint: Dict[str, Any]) -> str:
        """Serialize fingerprint to JSON string"""
        return json.dumps(fingerprint, sort_keys=True)

    def deserialize_fingerprint(self, fingerprint_str: str) -> Dict[str, Any]:
        """Deserialize fingerprint from JSON string"""
        return json.loads(fingerprint_str)

    def _hash_string(self, text: str) -> str:
        """Create SHA256 hash of a string"""
        return hashlib.sha256(text.encode()).hexdigest()

    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """Create SHA256 hash of a dictionary"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get_blockchain_payload(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract blockchain-ready payload for on-chain storage.
        Contains only essential verification data, not full fingerprint.
        """
        return {
            "blockchain_hash": fingerprint["blockchain_hash"],
            "timestamp": fingerprint["timestamp"],
            "version": fingerprint["version"],
            "image_hash": fingerprint["hashes"]["image_hash"],
            "metadata_hash": fingerprint["hashes"]["metadata_hash"],
            "features_hash": fingerprint["hashes"]["features_hash"]
        } 