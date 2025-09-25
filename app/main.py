from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Add startup validation
try:
    from app.api.endpoints import router
    from app.core.config import get_settings
    print("✅ Successfully imported all modules")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Medical Report Simplifier",
    description="AI-powered medical report processing with OCR, normalization, and patient-friendly explanations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup validation"""
    logger.info("🚀 Starting Medical Report Simplifier API")
    logger.info(f"📝 Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"🔑 GEMINI_API_KEY configured: {'Yes' if settings.gemini_api_key else 'No'}")
    logger.info(f"🏥 Health check available at: /api/v1/health")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Report Simplifier API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
