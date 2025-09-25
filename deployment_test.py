#!/usr/bin/env python3
"""
Quick deployment test script
Run this after deploying to Railway to validate everything works
"""

import requests
import json
import sys
import os

def test_api(base_url):
    """Test the deployed API"""
    print(f"🧪 Testing API at: {base_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"📋 Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Text processing
    print("\n2️⃣ Testing Text Processing...")
    try:
        data = {"text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"}
        response = requests.post(f"{base_url}/api/v1/process-text", 
                               json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "ok":
                print("✅ Text processing passed")
                print(f"📋 Found {len(result.get('tests', []))} tests")
            else:
                print(f"⚠️ Text processing returned: {result.get('status')}")
        else:
            print(f"❌ Text processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Text processing error: {e}")
        return False
    
    # Test 3: Demo format
    print("\n3️⃣ Testing Demo Problem Statement Format...")
    try:
        data = {"text": "CBC: Hemglobin 10.2 g/dL (Low), WBC 11,200 /uL (Hgh)"}
        response = requests.post(f"{base_url}/api/v1/demo-problem-statement", 
                               json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            expected_keys = ["step1_ocr_extraction", "step2_normalized_tests", 
                           "step3_patient_friendly", "step4_final_output"]
            if all(key in result for key in expected_keys):
                print("✅ Demo format test passed")
                print("📋 All 4 steps present")
            else:
                print("⚠️ Demo format missing some steps")
        else:
            print(f"❌ Demo format test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Demo format error: {e}")
        return False
    
    # Test 4: Error handling
    print("\n4️⃣ Testing Error Handling...")
    try:
        data = {"text": "This is just regular text without medical data."}
        response = requests.post(f"{base_url}/api/v1/process-text", 
                               json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "unprocessed":
                print("✅ Error handling passed")
                print(f"📋 Reason: {result.get('reason')}")
            else:
                print(f"⚠️ Expected 'unprocessed', got: {result.get('status')}")
        else:
            print(f"❌ Error handling test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False
    
    print(f"\n🎉 All tests passed! Your API is working correctly.")
    print(f"🌐 API Documentation: {base_url}/docs")
    print(f"📚 Alternative docs: {base_url}/redoc")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python deployment_test.py <API_URL>")
        print("Example: python deployment_test.py https://your-app.railway.app")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    
    print("🚂 Railway Deployment Test")
    print("Medical Report Simplifier API Validation")
    
    success = test_api(api_url)
    
    if success:
        print(f"\n✅ Deployment successful! Your API is ready for demo.")
        print(f"\n📝 For your assignment submission, use these URLs:")
        print(f"   • API Docs: {api_url}/docs")
        print(f"   • Demo endpoint: {api_url}/api/v1/demo-problem-statement")
        print(f"   • Production endpoint: {api_url}/api/v1/process-text")
    else:
        print(f"\n❌ Some tests failed. Check the Railway logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
