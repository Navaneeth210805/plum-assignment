#!/usr/bin/env python3
"""
Simple validation script to test the API against problem statement requirements
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_case(name, endpoint, data, expected_keys):
    print(f"\n🧪 Testing: {name}")
    print("-" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Status: {response.status_code}")
        
        # Check if expected keys exist
        missing_keys = [key for key in expected_keys if key not in result]
        if missing_keys:
            print(f"⚠️  Missing keys: {missing_keys}")
        else:
            print("✅ All expected keys present")
        
        # Pretty print result
        print(f"📋 Response:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("Medical Report Simplifier - Validation Tests")
    print("=" * 60)
    
    # Test 1: Basic text processing (Final Output)
    test_case(
        "Final Output Format",
        "process-text",
        {"text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"},
        ["tests", "summary", "status"]
    )
    
    # Test 2: Step-by-step demo (Problem Statement Format)
    test_case(
        "Problem Statement 4-Step Format",
        "demo-problem-statement", 
        {"text": "CBC: Hemglobin 10.2 g/dL (Low), WBC 11,200 /uL (Hgh)"},
        ["step1_ocr_extraction", "step2_normalized_tests", "step3_patient_friendly", "step4_final_output"]
    )
    
    # Test 3: Error case (should return unprocessed)
    test_case(
        "Error Handling - No Medical Data",
        "process-text",
        {"text": "This is just regular text without any medical information."},
        ["status", "reason"]
    )
    
    # Test 4: Detailed debug output
    test_case(
        "Debug Steps - Full Pipeline",
        "debug-steps",
        {"text": "CBC: Hemoglobin 8.5 g/dL (Low), WBC 15000 /uL (High)"},
        ["step1_ocr", "step2_normalization", "step3_summary", "step4_validation", "final_output"]
    )

if __name__ == "__main__":
    main()
