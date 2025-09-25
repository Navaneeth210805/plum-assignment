import pytest
from app.services.ai_service import AIService
from app.models.schemas import NormalizedTest, ReferenceRange, TestStatus


@pytest.fixture
def ai_service():
    """Create AIService instance for testing"""
    return AIService()


def test_validate_against_hallucination_valid_case(ai_service):
    """Test validation with correctly normalized data"""
    # Original test data
    original_tests = [
        "Hemoglobin 10.2 g/dL (Low)",
        "WBC 11200 /uL (High)",
        "Glucose 95 mg/dL (Normal)"
    ]
    
    # Correctly normalized tests
    normalized_tests = [
        NormalizedTest(
            name="Hemoglobin",
            value=10.2,
            unit="g/dL",
            status=TestStatus.LOW,
            ref_range=ReferenceRange(low=12.0, high=16.0)
        ),
        NormalizedTest(
            name="White Blood Cell Count",
            value=11200,
            unit="/uL",
            status=TestStatus.HIGH,
            ref_range=ReferenceRange(low=4000, high=11000)
        ),
        NormalizedTest(
            name="Glucose",
            value=95,
            unit="mg/dL",
            status=TestStatus.NORMAL,
            ref_range=ReferenceRange(low=70, high=100)
        )
    ]
    
    # This should pass validation
    is_valid, error_message = ai_service.validate_against_hallucination(
        original_tests, 
        normalized_tests
    )
    
    assert is_valid is True
    assert "passed" in error_message.lower()


def test_validate_against_hallucination_hallucinated_case(ai_service):
    """Test validation with hallucinated test data"""
    # Original test data - only has 2 tests
    original_tests = [
        "Hemoglobin 10.2 g/dL (Low)",
        "WBC 11200 /uL (High)"
    ]
    
    # Normalized tests with a hallucinated test (Cholesterol not in original)
    normalized_tests = [
        NormalizedTest(
            name="Hemoglobin",
            value=10.2,
            unit="g/dL",
            status=TestStatus.LOW,
            ref_range=ReferenceRange(low=12.0, high=16.0)
        ),
        NormalizedTest(
            name="White Blood Cell Count",
            value=11200,
            unit="/uL",
            status=TestStatus.HIGH,
            ref_range=ReferenceRange(low=4000, high=11000)
        ),
        NormalizedTest(
            name="Total Cholesterol",  # This is hallucinated!
            value=220,
            unit="mg/dL",
            status=TestStatus.HIGH,
            ref_range=ReferenceRange(low=0, high=200)
        )
    ]
    
    # This should fail validation due to hallucinated cholesterol test
    is_valid, error_message = ai_service.validate_against_hallucination(
        original_tests, 
        normalized_tests
    )
    
    assert is_valid is False
    assert len(error_message) > 0


def test_validate_against_hallucination_wrong_values(ai_service):
    """Test validation with incorrect values"""
    # Original test data
    original_tests = [
        "Hemoglobin 10.2 g/dL (Low)",
        "WBC 11200 /uL (High)"
    ]
    
    # Normalized tests with wrong values
    normalized_tests = [
        NormalizedTest(
            name="Hemoglobin",
            value=15.5,  # Wrong value! Original was 10.2
            unit="g/dL",
            status=TestStatus.NORMAL,
            ref_range=ReferenceRange(low=12.0, high=16.0)
        ),
        NormalizedTest(
            name="White Blood Cell Count",
            value=5000,  # Wrong value! Original was 11200
            unit="/uL",
            status=TestStatus.NORMAL,
            ref_range=ReferenceRange(low=4000, high=11000)
        )
    ]
    
    # This should fail validation due to wrong values
    is_valid, error_message = ai_service.validate_against_hallucination(
        original_tests, 
        normalized_tests
    )
    
    assert is_valid is False
    assert len(error_message) > 0


def test_validate_against_hallucination_empty_data(ai_service):
    """Test validation with empty data"""
    # Test with empty original tests
    is_valid, error_message = ai_service.validate_against_hallucination(
        [], 
        []
    )
    
    assert is_valid is False
    assert "no data" in error_message.lower()


if __name__ == "__main__":
    # Simple test runner
    print("Testing AI-powered hallucination validation...")
    
    try:
        ai_service = AIService()
        
        # Test valid case
        print("\n1. Testing valid normalization...")
        original = ["Hemoglobin 10.2 g/dL (Low)", "WBC 11200 /uL (High)"]
        normalized = [
            NormalizedTest(
                name="Hemoglobin",
                value=10.2,
                unit="g/dL", 
                status=TestStatus.LOW,
                ref_range=ReferenceRange(low=12.0, high=16.0)
            )
        ]
        
        is_valid, message = ai_service.validate_against_hallucination(original, normalized)
        print(f"Valid case result: {is_valid}, Message: {message}")
        
        # Test hallucination case
        print("\n2. Testing hallucinated test...")
        hallucinated = [
            NormalizedTest(
                name="Total Cholesterol",  # Not in original!
                value=220,
                unit="mg/dL",
                status=TestStatus.HIGH,
                ref_range=ReferenceRange(low=0, high=200)
            )
        ]
        
        is_valid, message = ai_service.validate_against_hallucination(original, hallucinated)
        print(f"Hallucination case result: {is_valid}, Message: {message}")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
