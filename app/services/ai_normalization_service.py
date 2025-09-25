import re
from typing import List, Optional, Tuple
from app.models.schemas import NormalizedTest, NormalizationResult
from app.services.ai_service import AIService


class AINormalizationService:
    def __init__(self):
        self.ai_service = AIService()
    
    def normalize_single_test(self, test_string: str) -> Optional[NormalizedTest]:
        """Normalize a single test result using AI"""
        
        ai_data = self.ai_service.normalize_test_with_ai(test_string)
        if ai_data:
            return self.ai_service.create_normalized_test_from_ai(ai_data)
        
        return None
    
    def calculate_normalization_confidence(self, raw_tests: List[str], normalized_tests: List[NormalizedTest]) -> float:
        """Calculate confidence score for normalization process"""
        if not raw_tests:
            return 0.0
        
        # Base confidence on successful normalization rate
        success_rate = len(normalized_tests) / len(raw_tests)
        
        # Higher confidence for AI-powered normalization
        base_confidence = 0.85 + (success_rate * 0.1)  # 85-95% base confidence
        
        return min(base_confidence, 0.95)  # Cap at 95%
    
    def validate_tests(self, tests: List[NormalizedTest]) -> Tuple[bool, Optional[str]]:
        """Validate normalized tests for hallucination and errors"""
        
        if not tests:
            return False, "No valid tests found in input"
        
        # Check for unrealistic values that might indicate hallucination
        for test in tests:
            # Check if value is extremely outside normal ranges (potential hallucination)
            if test.value < 0:
                return False, f"Invalid negative value for {test.name}"
            
            # Check for extremely unrealistic values based on test type
            test_name_lower = test.name.lower()
            
            if 'hemoglobin' in test_name_lower and (test.value > 30 or test.value < 1):
                return False, f"Unrealistic {test.name} value: {test.value}"
            
            if 'wbc' in test_name_lower or 'white blood' in test_name_lower:
                if test.value > 200000 or test.value < 50:
                    return False, f"Unrealistic {test.name} value: {test.value}"
            
            if 'glucose' in test_name_lower and (test.value > 1000 or test.value < 10):
                return False, f"Unrealistic {test.name} value: {test.value}"
        
        return True, None
    
    def normalize_tests(self, raw_tests: List[str]) -> NormalizationResult:
        """Normalize a list of raw test strings using AI"""
        
        if not raw_tests:
            return NormalizationResult(tests=[], normalization_confidence=0.0)
        
        normalized_tests = []
        
        for test_string in raw_tests:
            normalized_test = self.normalize_single_test(test_string)
            if normalized_test:
                normalized_tests.append(normalized_test)
        
        # Remove duplicates based on test name and value
        unique_tests = []
        seen = set()
        for test in normalized_tests:
            test_key = (test.name.lower(), test.value, test.unit.lower())
            if test_key not in seen:
                unique_tests.append(test)
                seen.add(test_key)
        
        # Calculate confidence
        confidence = self.calculate_normalization_confidence(raw_tests, unique_tests)
        
        return NormalizationResult(
            tests=unique_tests,
            normalization_confidence=confidence
        )


# Global instance
ai_normalization_service = AINormalizationService()
