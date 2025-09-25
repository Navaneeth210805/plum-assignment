import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Union
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("python-magic not available, using basic file validation")
from io import BytesIO
from PIL import Image

from app.models.schemas import (
    TextInput, FinalOutput, ErrorResponse, ProcessingResponse
)
from app.services.processing_service import processing_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

settings = get_settings()


def get_mime_type(file_content: bytes, filename: str = None) -> str:
    """Get MIME type with fallback when magic is not available"""
    if MAGIC_AVAILABLE:
        try:
            return magic.from_buffer(file_content, mime=True)
        except Exception:
            pass
    
    # Fallback: basic extension checking
    if filename:
        filename_lower = filename.lower()
        if filename_lower.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg'
        elif filename_lower.endswith('.png'):
            return 'image/png'
        elif filename_lower.endswith('.gif'):
            return 'image/gif'
        elif filename_lower.endswith('.bmp'):
            return 'image/bmp'
        elif filename_lower.endswith('.tiff', '.tif'):
            return 'image/tiff'
    
    # Try to validate by opening with PIL
    try:
        Image.open(BytesIO(file_content))
        return 'image/unknown'  # Valid image but unknown specific type
    except Exception:
        return 'application/octet-stream'


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    from app.core.config import get_settings
    
    settings = get_settings()
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "environment": {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "port": os.getenv("PORT", "8000"),
            "gemini_configured": bool(settings.gemini_api_key and settings.gemini_api_key.strip()),
            "magic_available": MAGIC_AVAILABLE
        }
    }


@router.post("/process-text")
async def process_text(text_input: TextInput):
    """Process medical report text input"""
    try:
        logger.info("Processing text input")
        print("Processing text input")
        
        # Process through the complete pipeline
        result = processing_service.process_text_input(text_input.text)
        
        return result
        
    except Exception as e:
        logger.error(f"Text processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during text processing")


@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    """Process medical report image input"""
    try:
        logger.info(f"Processing image input: {file.filename}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Validate MIME type
        mime_type = get_mime_type(file_content, file.filename)
        if not mime_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File is not a valid image")
        
        # Convert to PIL Image
        try:
            image = Image.open(BytesIO(file_content))
            image = image.convert('RGB')  # Ensure RGB format
        except Exception as e:
            raise HTTPException(status_code=400, detail="Unable to process image file")
        
        # Process through the complete pipeline
        result = processing_service.process_image_input(image)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during image processing")


@router.post("/debug-steps")
async def debug_processing_steps(text_input: TextInput = None):
    """Debug endpoint to see step-by-step processing results"""
    try:
        if text_input and text_input.text:
            return processing_service.get_step_by_step_results(text=text_input.text)
        else:
            raise HTTPException(status_code=400, detail="Provide text input")
            
    except Exception as e:
        logger.error(f"Debug processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug processing error: {str(e)}")


@router.post("/debug-steps-image")
async def debug_processing_steps_image(file: UploadFile = File(...)):
    """Debug endpoint to see step-by-step processing results for image"""
    try:
        file_content = await file.read()
        image = Image.open(BytesIO(file_content)).convert('RGB')
        return processing_service.get_step_by_step_results(image=image)
            
    except Exception as e:
        logger.error(f"Debug image processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug processing error: {str(e)}")


@router.post("/demo-problem-statement")
async def demo_problem_statement_format(text_input: TextInput):
    """Demo endpoint showing exact format from problem statement"""
    try:
        result = processing_service.get_step_by_step_results(text=text_input.text)
        
        # Format exactly as problem statement expects
        demo_response = {}
        
        if "step1_ocr" in result:
            demo_response["step1_ocr_extraction"] = result["step1_ocr"]
        
        if "step2_normalization" in result:
            demo_response["step2_normalized_tests"] = result["step2_normalization"]
        
        if "step3_summary" in result:
            demo_response["step3_patient_friendly"] = result["step3_summary"]
        
        if "final_output" in result:
            demo_response["step4_final_output"] = result["final_output"]
        
        return demo_response
        
    except Exception as e:
        logger.error(f"Demo processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo processing error: {str(e)}")
