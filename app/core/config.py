import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    def __init__(self):
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "AIzaSyC-6VoL22oqlIOXC-hmIqSK3Eo_tv3MXQQ")
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        # OCR settings
        self.ocr_confidence_threshold: float = 0.5
        
        # AI settings
        self.ai_temperature: float = 0.1
        self.max_tokens: int = 1000
        
        # Validation settings
        self.validation_confidence_threshold: float = float(
            os.getenv("VALIDATION_CONFIDENCE_THRESHOLD", "0.7")
        )
        
        # File upload settings
        self.max_file_size: int = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions: list = [".png", ".jpg", ".jpeg", ".pdf"]


def get_settings():
    """Get settings instance"""
    return Settings()
