# Railway deployment requirements
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Environment variables needed on Railway:
# GEMINI_API_KEY=your_gemini_api_key_here
# AI_TEMPERATURE=0.3  
# VALIDATION_CONFIDENCE_THRESHOLD=0.7
# MAX_FILE_SIZE=10485760

# Railway will automatically install system dependencies including:
# - Python 3.9+
# - Tesseract OCR
# - Required system libraries for image processing
