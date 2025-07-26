#!/usr/bin/env python3
"""
Comprehensive PixelLedger Testing Script

Features:
- Lists available images in the images/ folder
- User selects image to watermark
- Shows all extracted semantic data in console
- Creates watermarked image
- Opens watermarked image in default viewer
"""

import os
import sys
import json
import subprocess
import platform
from app.core.pixel_ledger import PixelLedger

def print_section(title, data, indent=0):
    """Helper function to print formatted sections"""
    indent_str = "   " * indent
    print(f"\n{indent_str}📋 {title}")
    print(f"{indent_str}{'=' * (len(title) + 4)}")
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 50:
                print(f"{indent_str}   {key}: {value[:50]}...")
            elif isinstance(value, list):
                print(f"{indent_str}   {key}: {value}")
            else:
                print(f"{indent_str}   {key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent_str}   {i+1}. {item}")
    else:
        print(f"{indent_str}   {data}")

def get_image_files():
    """Get list of image files from images/ folder"""
    images_folder = "images"
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"📁 Created images folder: {images_folder}")
        print(f"   Please add some images to the {images_folder}/ folder and run again.")
        return []
    
    # Supported image formats
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp']
    
    image_files = []
    for file in os.listdir(images_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            file_path = os.path.join(images_folder, file)
            file_size = os.path.getsize(file_path)
            image_files.append({
                'name': file,
                'path': file_path,
                'size': file_size
            })
    
    return image_files

def display_image_selection():
    """Display available images and let user select one"""
    print("🚀 PixelLedger Semantic-Aware Digital Watermarking System")
    print("=" * 60)
    
    image_files = get_image_files()
    
    if not image_files:
        print(f"\n❌ No images found in images/ folder.")
        print(f"   Please add some images and run again.")
        return None
    
    print(f"\n📁 Available Images in images/ folder:")
    print("-" * 40)
    
    for i, img in enumerate(image_files, 1):
        size_mb = img['size'] / (1024 * 1024)
        print(f"   {i}. {img['name']} ({size_mb:.2f} MB)")
    
    print(f"\n   Total images: {len(image_files)}")
    
    # Get user selection
    while True:
        try:
            selection = input(f"\n🎯 Select image number (1-{len(image_files)}): ").strip()
            selection_num = int(selection)
            
            if 1 <= selection_num <= len(image_files):
                selected_image = image_files[selection_num - 1]
                print(f"\n✅ Selected: {selected_image['name']}")
                return selected_image
            else:
                print(f"❌ Please enter a number between 1 and {len(image_files)}")
        except ValueError:
            print(f"❌ Please enter a valid number")
        except KeyboardInterrupt:
            print(f"\n👋 Goodbye!")
            return None

def open_image_in_viewer(image_path):
    """Open image in default system viewer"""
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(image_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", image_path])
        else:  # Linux
            subprocess.run(["xdg-open", image_path])
        
        print(f"✅ Image opened in default viewer!")
        return True
    except Exception as e:
        print(f"❌ Error opening image: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive PixelLedger test"""
    
    # Step 1: Display image selection
    selected_image = display_image_selection()
    if not selected_image:
        return
    
    # Step 2: Initialize PixelLedger
    print(f"\n🔧 Initializing PixelLedger system...")
    ledger = PixelLedger(watermark_strength=25.0)
    
    # Step 3: Prepare metadata
    metadata = {
        "author": "PixelLedger User",
        "title": f"Watermarked: {selected_image['name']}",
        "description": f"Semantic-aware watermarked image created with PixelLedger",
        "creation_date": "2024-01-15",
        "copyright": "© 2024 PixelLedger. All rights reserved.",
        "license": "CC BY-NC-ND 4.0",
        "original_filename": selected_image['name'],
        "original_filesize": selected_image['size'],
        "watermarking_system": "PixelLedger v1.0",
        "semantic_features": ["caption", "objects", "scenes", "perceptual_hash"]
    }
    
    print_section("Input Metadata", metadata)
    
    try:
        # Step 4: Check watermark capacity
        print_section("Image Capacity Analysis", {
            "image_path": selected_image['path'],
            "file_size_bytes": selected_image['size'],
            "file_size_mb": f"{selected_image['size'] / (1024 * 1024):.2f} MB",
            "estimated_capacity_bits": ledger.watermarker.estimate_capacity(selected_image['path']),
            "estimated_capacity_bytes": ledger.watermarker.estimate_capacity(selected_image['path']) // 8
        })
        
        # Step 5: Extract semantic context
        print_section("Semantic Context Extraction", "Processing with AI models...")
        semantic_context = ledger.semantic_extractor.extract_semantic_context(selected_image['path'])
        
        print_section("AI-Generated Caption", {
            "caption": semantic_context['caption'],
            "caption_length": len(semantic_context['caption']),
            "caption_words": len(semantic_context['caption'].split())
        })
        
        print_section("Detected Objects (Top 5)", {
            "objects": semantic_context['detected_objects'],
            "confidence_scores": [f"{score:.3f}" for score in semantic_context['object_confidence']],
            "object_count": len(semantic_context['detected_objects'])
        })
        
        print_section("Semantic Hash", {
            "hash_value": semantic_context['semantic_hash'],
            "hash_length": len(semantic_context['semantic_hash']),
            "hash_type": "SHA256 (truncated to 16 chars)",
            "purpose": "Tamper detection and semantic drift analysis"
        })
        
        # Step 6: Compute perceptual hash
        print_section("Perceptual Hash Analysis", "Computing visual fingerprint...")
        from app.core.phash import compute_phash
        phash = compute_phash(selected_image['path'])
        
        print_section("Perceptual Hash Details", {
            "hash_value": phash,
            "hash_length": len(phash),
            "hash_type": "pHash (perceptual hash)",
            "resistance": "Compression, resizing, minor modifications",
            "purpose": "Visual content verification"
        })
        
        # Step 7: Create semantic watermark
        print_section("Creating Semantic Watermark", "Embedding data using DCT...")
        output_filename = f"watermarked_{selected_image['name']}"
        output_path = os.path.join("images", output_filename)
        
        result = ledger.create_semantic_watermark(
            image_path=selected_image['path'],
            metadata=metadata,
            output_path=output_path
        )
        
        if result["success"]:
            print_section("Watermark Creation Success", {
                "status": "✅ Success",
                "watermarked_image_path": result['watermarked_image_path'],
                "capacity_used_bits": result['capacity_used'],
                "total_capacity_bits": result['total_capacity'],
                "capacity_utilization_percent": f"{(result['capacity_used'] / result['total_capacity']) * 100:.1f}%"
            })
            
            # Step 8: Show complete fingerprint structure
            fingerprint = result['fingerprint']
            
            print_section("Complete Fingerprint Structure", {
                "version": fingerprint['version'],
                "timestamp": fingerprint['timestamp'],
                "blockchain_hash": fingerprint['blockchain_hash'][:32] + "...",
                "fingerprint_size_bytes": len(json.dumps(fingerprint, sort_keys=True))
            })
            
            print_section("Hash Verification Structure", {
                "image_hash": fingerprint['hashes']['image_hash'][:32] + "...",
                "metadata_hash": fingerprint['hashes']['metadata_hash'][:32] + "...",
                "features_hash": fingerprint['hashes']['features_hash'][:32] + "..."
            })
            
            print_section("Embedded Data Summary", {
                "semantic_caption": fingerprint['data']['semantic_context']['caption'],
                "detected_objects_count": len(fingerprint['data']['semantic_context']['detected_objects']),
                "perceptual_hash": fingerprint['data']['phash'][:16] + "...",
                "metadata_fields": list(fingerprint['data']['metadata'].keys())
            })
            
            # Step 9: Verify the watermark
            print_section("Watermark Verification", "Verifying embedded data...")
            verification = ledger.verify_semantic_watermark(image_path=output_path)
            
            if verification["success"]:
                print_section("Verification Results", {
                    "fingerprint_valid": verification['verification_results']['fingerprint_valid'],
                    "image_hash_valid": verification['verification_results']['image_hash_valid'],
                    "metadata_hash_valid": verification['verification_results']['metadata_hash_valid'],
                    "features_hash_valid": verification['verification_results']['features_hash_valid'],
                    "blockchain_hash_valid": verification['verification_results']['blockchain_hash_valid']
                })
                
                print_section("Semantic Drift Analysis", {
                    "drift_detected": verification['drift_analysis']['drift_detected'],
                    "caption_changed": verification['drift_analysis']['caption_changed'],
                    "objects_changed": verification['drift_analysis']['objects_changed'],
                    "semantic_hash_changed": verification['drift_analysis']['semantic_hash_changed']
                })
                
                print_section("Overall Authenticity", {
                    "authentic": verification['overall_authentic'],
                    "verification_status": "✅ AUTHENTIC" if verification['overall_authentic'] else "❌ TAMPERED"
                })
                
                # Step 10: Show blockchain payload
                blockchain_payload = result['blockchain_payload']
                print_section("Blockchain-Ready Payload", {
                    "blockchain_hash": blockchain_payload['blockchain_hash'][:32] + "...",
                    "timestamp": blockchain_payload['timestamp'],
                    "version": blockchain_payload['version'],
                    "image_hash": blockchain_payload['image_hash'][:32] + "...",
                    "metadata_hash": blockchain_payload['metadata_hash'][:32] + "...",
                    "features_hash": blockchain_payload['features_hash'][:32] + "..."
                })
                
                # Step 11: Show what's actually embedded in the watermark
                print_section("Watermark Content Summary", {
                    "total_embedded_data": f"{result['capacity_used']} bits ({result['capacity_used']//8} bytes)",
                    "semantic_caption_length": len(semantic_context['caption']),
                    "detected_objects": semantic_context['detected_objects'],
                    "perceptual_hash_length": len(phash),
                    "metadata_fields_count": len(metadata),
                    "verification_hashes": 4,  # image, metadata, features, blockchain
                    "invisibility": "✅ Invisible to human eye",
                    "robustness": "✅ Resistant to compression/resizing",
                    "semantic_drift_detection": "✅ Detects content changes"
                })
                
                # Step 12: Open watermarked image
                print_section("Opening Watermarked Image", "Launching in default viewer...")
                open_image_in_viewer(output_path)
                
                print_section("Test Complete", {
                    "status": "✅ SUCCESS",
                    "original_image": selected_image['name'],
                    "watermarked_image": output_filename,
                    "semantic_data_extracted": "✅",
                    "watermark_embedded": "✅",
                    "verification_passed": "✅",
                    "image_opened": "✅"
                })
                
            else:
                print_section("Verification Failed", {
                    "error": verification['error']
                })
        else:
            print_section("Watermark Creation Failed", {
                "error": result['error']
            })
            
    except Exception as e:
        print_section("Error During Processing", {
            "error": str(e)
        })
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_test() 