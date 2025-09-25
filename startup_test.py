#!/usr/bin/env python3
"""
Simple startup test to validate the application can import and start
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/app')

def test_imports():
    """Test that all imports work"""
    try:
        print("Testing imports...")
        
        # Test core imports
        from app.core.config import get_settings
        print("✅ Config import successful")
        
        # Test models
        from app.models.schemas import TextInput, FinalOutput
        print("✅ Models import successful")
        
        # Test services
        from app.services.ocr_service import ocr_service
        print("✅ OCR service import successful")
        
        from app.services.ai_service import AIService
        print("✅ AI service import successful")
        
        from app.services.processing_service import processing_service
        print("✅ Processing service import successful")
        
        # Test API
        from app.api.endpoints import router
        print("✅ API endpoints import successful")
        
        # Test main app
        from app.main import app
        print("✅ Main app import successful")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test that the health endpoint is accessible"""
    try:
        from app.main import app
        # Check if fastapi TestClient is available
        try:
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/api/v1/health")
            
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Health endpoint failed with status {response.status_code}")
                return False
        except ImportError:
            # TestClient not available, just check that app can be created
            print("✅ App created successfully (TestClient not available)")
            return True
            
    except Exception as e:
        print(f"❌ Health endpoint test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting application validation...")
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test health endpoint
    if not test_health_endpoint():
        sys.exit(1)
    
    print("✅ All tests passed! Application should start successfully.")
