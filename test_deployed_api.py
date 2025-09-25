#!/usr/bin/env python3
"""
Sample client to test the deployed Medical Report Simplifier API
Replace BASE_URL with your actual Railway app URL
"""
import requests
import json

# Replace with your actual Railway URL
BASE_URL = "https://your-app-name.railway.app"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Health Check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_text_processing():
    """Test text processing endpoint"""
    try:
        sample_text = """
        Laboratory Results:
        Complete Blood Count (CBC):
        - White Blood Cell Count: 7,500 cells/μL (Normal: 4,000-11,000)
        - Red Blood Cell Count: 4.2 million cells/μL (Normal: 3.8-5.2)
        - Hemoglobin: 13.8 g/dL (Normal: 12-16)
        - Hematocrit: 40% (Normal: 36-46%)
        
        Basic Metabolic Panel:
        - Glucose: 95 mg/dL (Normal: 70-100)
        - Sodium: 140 mEq/L (Normal: 135-145)
        - Potassium: 4.0 mEq/L (Normal: 3.5-5.0)
        """
        
        response = requests.post(
            f"{BASE_URL}/api/v1/process-text",
            json={"text": sample_text.strip()},
            timeout=30
        )
        
        print(f"Text Processing: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Text processing successful!")
            print(f"Summary: {result.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"Text processing failed: {e}")

def test_debug_endpoint():
    """Test debug endpoint to see step-by-step results"""
    try:
        sample_text = "CBC: WBC 7500, RBC 4.2M, Hemoglobin 13.8 g/dL"
        
        response = requests.post(
            f"{BASE_URL}/api/v1/debug-steps",
            json={"text": sample_text},
            timeout=30
        )
        
        print(f"Debug Steps: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Debug processing successful!")
            for step, data in result.items():
                print(f"  {step}: {str(data)[:50]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"Debug test failed: {e}")

def main():
    print(f"🧪 Testing Medical Report Simplifier API at: {BASE_URL}")
    print("=" * 60)
    
    # Test health
    print("\n1. Testing Health Endpoint...")
    if not test_health():
        print("❌ Health check failed. Please check your BASE_URL.")
        return
    
    # Test text processing
    print("\n2. Testing Text Processing...")
    test_text_processing()
    
    # Test debug endpoint
    print("\n3. Testing Debug Endpoint...")
    test_debug_endpoint()
    
    print(f"\n🌐 Visit {BASE_URL}/docs for interactive API documentation!")

if __name__ == "__main__":
    main()
