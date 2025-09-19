from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json
import uuid
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the watermarking module to the path
watermarking_path = Path(__file__).parent.parent / "watermarking"
sys.path.append(str(watermarking_path))

from app.core.pixel_ledger import PixelLedger

app = FastAPI(
    title="PixelLedger API",
    description="Semantic-aware digital watermarking with blockchain binding",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("watermarked", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize PixelLedger
pixel_ledger = PixelLedger()

@app.get("/")
async def root():
    return {"message": "PixelLedger API is running", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "system": "PixelLedger API"}

@app.post("/api/check-watermark")
async def check_watermark(file: UploadFile = File(...)):
    """
    Check if an image already contains a watermark
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Try to extract watermark
            verification_result = pixel_ledger.verify_semantic_watermark(file_path)
            
            # Clean up temporary file
            os.remove(file_path)
            
            return {
                "hasWatermark": verification_result.get("success", False),
                "isTampered": not verification_result.get("overall_authentic", False) if verification_result.get("success") else False,
                "details": verification_result
            }
            
        except Exception as e:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {
                "hasWatermark": False,
                "isTampered": False,
                "error": str(e)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking watermark: {str(e)}")

@app.post("/api/create-watermark")
async def create_watermark(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):
    """
    Create a semantic watermark for an uploaded image
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Generate output path
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"watermarked_{base_name}_{file_id}.png"
        output_path = f"watermarked/{output_filename}"
        
        # Create watermark
        result = pixel_ledger.create_semantic_watermark(
            image_path=file_path,
            metadata=metadata_dict,
            output_path=output_path
        )
        
        # Clean up input file
        os.remove(file_path)
        
        if result["success"]:
            # Generate URL for the watermarked image
            watermarked_url = f"/static/{output_filename}"
            
            # Copy watermarked image to static directory for serving
            static_path = f"static/{output_filename}"
            os.rename(output_path, static_path)
            
            return {
                "success": True,
                "watermarked_image_url": watermarked_url,
                "fingerprint": result["fingerprint"],
                "semantic_context": result["semantic_context"],
                "phash": result["phash"],
                "capacity_used": result["capacity_used"],
                "total_capacity": result["total_capacity"],
                "blockchain_payload": result["blockchain_payload"]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create watermark"))
            
    except HTTPException:
        raise
    except Exception as e:
        # Clean up files on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)
        
        raise HTTPException(status_code=500, detail=f"Error creating watermark: {str(e)}")

@app.post("/api/verify-watermark")
async def verify_watermark(file: UploadFile = File(...)):
    """
    Verify a watermark in an uploaded image
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Verify watermark
            verification_result = pixel_ledger.verify_semantic_watermark(file_path)
            
            # Clean up temporary file
            os.remove(file_path)
            
            return verification_result
            
        except Exception as e:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {
                "success": False,
                "error": str(e)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying watermark: {str(e)}")

@app.get("/api/system-info")
async def get_system_info():
    """
    Get system information and capabilities
    """
    return pixel_ledger.get_system_info()

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download a watermarked image file
    """
    file_path = f"static/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
