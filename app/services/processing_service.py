from typing import Union, List
from PIL import Image
from app.models.schemas import (
    FinalOutput, ErrorResponse, ProcessingStatus, 
    OCRResult, NormalizationResult, PatientFriendlySummary
)
from app.services.ocr_service import ocr_service
from app.services.ai_normalization_service import ai_normalization_service
from app.services.ai_service import AIService

class ProcessingService:
    def __init__(self):
        self.ocr_service = ocr_service
        self.ai_normalization_service = ai_normalization_service
        self.ai_service = AIService()
    
    def process_text_input(self, text: str) -> Union[FinalOutput, ErrorResponse]:
        """Process text input through the 4-step pipeline"""
        try:
            # Step 1: OCR/Text Extraction (for text input, this is just cleaning)
            ocr_result = self.ocr_service.process_text_input(text)
            print("OCR Result:", ocr_result)
            
            if not ocr_result.tests_raw:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason="No medical tests found in input text"
                )
                
            # Fix ocr error using ai service to make it more generalized
            ocr_result.tests_raw = self.ai_service.fix_ocr_errors(ocr_result.tests_raw)
            print("Fixed OCR Result:", ocr_result)
            
            
            # Step 2: AI-powered Normalization
            normalization_result = self.ai_normalization_service.normalize_tests(ocr_result.tests_raw)
            
            if not normalization_result.tests:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason="Unable to normalize any tests from input"
                )
            
            # Validate for hallucination using AI-powered semantic comparison
            is_valid, validation_error = self.ai_service.validate_against_hallucination(
                ocr_result.tests_raw, 
                normalization_result.tests
            )
            
            if not is_valid:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason=f"Validation failed - possible hallucination: {validation_error}"
                )
            
            # Step 3: Patient-Friendly Summary
            summary = self.ai_service.generate_patient_summary(normalization_result.tests)
            
            # Step 4: Final Output
            return FinalOutput(
                tests=normalization_result.tests,
                summary=summary.summary,
                explanations=summary.explanations,
                status=ProcessingStatus.OK
            )
            
        except Exception as e:
            return ErrorResponse(
                status=ProcessingStatus.ERROR,
                reason=f"Processing error: {str(e)}"
            )
    
    def process_image_input(self, image: Image.Image) -> Union[FinalOutput, ErrorResponse]:
        """Process image input through the 4-step pipeline"""
        try:
            # Step 1: OCR/Text Extraction
            ocr_result = self.ocr_service.process_image_input(image)
            
            # if not ocr_result.tests_raw or ocr_result.confidence < 0.3:
            #     return ErrorResponse(
            #         status=ProcessingStatus.UNPROCESSED,
            #         reason="OCR failed to extract readable medical tests from image"
            #     )
                
            ocr_result.tests_raw = self.ai_service.fix_ocr_errors(ocr_result.tests_raw)
            print("Fixed OCR Result:", ocr_result)
            
            # Step 2: AI-powered Normalization
            normalization_result = self.ai_normalization_service.normalize_tests(ocr_result.tests_raw)
            
            if not normalization_result.tests:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason="Unable to normalize any tests from OCR output"
                )
            
            # Validate for hallucination using AI-powered semantic comparison
            is_valid, validation_error = self.ai_service.validate_against_hallucination(
                ocr_result.tests_raw, 
                normalization_result.tests
            )
            
            if not is_valid:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason=f"Validation failed - possible hallucination: {validation_error}"
                )
            
            # Step 3: Patient-Friendly Summary
            summary = self.ai_service.generate_patient_summary(normalization_result.tests)
            
            # Step 4: Final Output
            return FinalOutput(
                tests=normalization_result.tests,
                summary=summary.summary,
                explanations=summary.explanations,
                status=ProcessingStatus.OK
            )
            
        except Exception as e:
            return ErrorResponse(
                status=ProcessingStatus.ERROR,
                reason=f"Processing error: {str(e)}"
            )
    
    def get_step_by_step_results(self, text: str = None, image: Image.Image = None) -> dict:
        """Get detailed results from each processing step (for debugging/demo purposes)"""
        try:
            results = {}
            
            # Step 1: OCR/Text Extraction
            if text:
                ocr_result = self.ocr_service.process_text_input(text)
            elif image:
                ocr_result = self.ocr_service.process_image_input(image)
            else:
                return {"error": "No input provided"}
            
            results["step1_ocr"] = {
                "tests_raw": ocr_result.tests_raw,
                "confidence": ocr_result.confidence
            }
            
            # Step 1b: OCR Error Fixing
            if ocr_result.tests_raw:
                fixed_tests = self.ai_service.fix_ocr_errors(ocr_result.tests_raw)
                results["step1b_ocr_fix"] = {
                    "tests_raw_fixed": fixed_tests,
                    "ocr_errors_fixed": len(fixed_tests) > 0
                }
                ocr_result.tests_raw = fixed_tests
            
            if not ocr_result.tests_raw:
                return results
            
            # Step 2: AI-powered Normalization
            normalization_result = self.ai_normalization_service.normalize_tests(ocr_result.tests_raw)
            results["step2_normalization"] = {
                "tests": [test.dict() for test in normalization_result.tests],
                "normalization_confidence": normalization_result.normalization_confidence
            }
            
            if not normalization_result.tests:
                return results
            
            # Step 3: Patient-Friendly Summary
            summary = self.ai_service.generate_patient_summary(normalization_result.tests)
            results["step3_summary"] = {
                "summary": summary.summary,
                "explanations": summary.explanations
            }
            
            # Step 4: AI-powered hallucination validation
            is_valid, validation_error = self.ai_service.validate_against_hallucination(
                ocr_result.tests_raw, 
                normalization_result.tests
            )
            results["step4_validation"] = {
                "is_valid": is_valid,
                "validation_error": validation_error,
                "validation_method": "AI semantic comparison"
            }
            
            # Final result in exact format as problem statement
            if is_valid:
                results["final_output"] = {
                    "tests": [test.dict() for test in normalization_result.tests],
                    "summary": summary.summary,
                    "status": "ok"
                }
            else:
                results["final_output"] = {
                    "status": "unprocessed",
                    "reason": f"hallucinated tests not present in input: {validation_error}"
                }
            
            return results
            
        except Exception as e:
            return {"error": f"Step-by-step processing error: {str(e)}"}


# Global instance
processing_service = ProcessingService()
