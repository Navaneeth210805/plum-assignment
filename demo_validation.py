#!/usr/bin/env python3.9
"""
Demo script showing AI-powered hallucination validation in action
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.processing_service import processing_service


def demo_validation():
    """Demonstrate the AI-powered validation approach"""
    
    print("🔍 AI-Powered Hallucination Validation Demo")
    print("=" * 50)
    
    # Test Case 1: Valid input that should pass validation
    print("\n📋 Test Case 1: Valid Medical Report")
    print("-" * 30)
    
    valid_text = """
    Complete Blood Count (CBC):
    Hemoglobin: 10.2 g/dL (Low)
    White Blood Cell Count: 11,200 /uL (High)  
    Platelet Count: 350,000 /uL (Normal)
    """
    
    print(f"Input: {valid_text.strip()}")
    
    result = processing_service.process_text_input(valid_text)
    
    if hasattr(result, 'status') and result.status.value == 'ok':
        print("✅ Validation PASSED - No hallucination detected")
        print(f"📊 Found {len(result.tests)} tests:")
        for test in result.tests:
            print(f"   - {test.name}: {test.value} {test.unit} ({test.status.value})")
    else:
        print(f"❌ Processing failed: {result.reason}")
    
    # Test Case 2: Input designed to potentially cause hallucination
    print("\n📋 Test Case 2: Ambiguous/Unclear Input")
    print("-" * 30)
    
    ambiguous_text = """
    Blood work results:
    Hgb low at 10
    Some white cells elevated  
    """
    
    print(f"Input: {ambiguous_text.strip()}")
    
    result = processing_service.process_text_input(ambiguous_text)
    
    if hasattr(result, 'status') and result.status.value == 'ok':
        print("✅ Validation PASSED")
        print(f"📊 Found {len(result.tests)} tests:")
        for test in result.tests:
            print(f"   - {test.name}: {test.value} {test.unit} ({test.status.value})")
    else:
        print(f"❌ Validation FAILED: {result.reason}")
    
    # Test Case 3: Get step-by-step breakdown
    print("\n🔬 Step-by-Step Processing Breakdown")
    print("-" * 30)
    
    steps = processing_service.get_step_by_step_results(text=valid_text)
    
    if "error" not in steps:
        for step_name, step_data in steps.items():
            print(f"\n{step_name.upper().replace('_', ' ')}:")
            if step_name == "step4_validation":
                print(f"   Valid: {step_data.get('is_valid', 'Unknown')}")
                print(f"   Method: {step_data.get('validation_method', 'Unknown')}")
                if step_data.get('validation_error'):
                    print(f"   Details: {step_data['validation_error']}")
            else:
                print(f"   {step_data}")
    
    print("\n" + "=" * 50)
    print("💡 How AI Validation Works:")
    print("1. Compares original text with normalized results")
    print("2. Checks for semantic consistency using AI")
    print("3. Detects fabricated tests, wrong values, or hallucinations") 
    print("4. Uses confidence scoring for reliability")
    print("5. Allows reasonable medical standardization")


if __name__ == "__main__":
    try:
        demo_validation()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nMake sure you have:")
        print("- Set up your GEMINI_API_KEY environment variable")
        print("- Installed all required dependencies")