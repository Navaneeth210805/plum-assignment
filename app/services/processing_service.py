from typing import Union
from PIL import Image
from app.models.schemas import (
    FinalOutput, ErrorResponse, ProcessingStatus
)
from app.services.ocr_service import ocr_service
from app.services.ai_service import AIService

class ProcessingService:
    def __init__(self):
        self.ocr_service = ocr_service
        self.ai_service = AIService()

    def process_text_input(self, text: str) -> Union[FinalOutput, ErrorResponse]:
        """Process text input (OCR cleanup + single AI call for normalization/validation/summary)."""
        try:
            # Step 1: OCR cleaning
            ocr_result = self.ocr_service.process_text_input(text)
            if not ocr_result.tests_raw:
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason="No tests found in input text"
                )

            fixed_tests = self.ai_service.fix_ocr_errors(ocr_result.tests_raw)

            # Step 2-4: Single AI call
            ai_data = self.ai_service.process_tests(fixed_tests)

            if not ai_data.get("validation", {}).get("is_valid", False):
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason=f"Validation failed: {ai_data['validation'].get('explanation', 'Unknown')}"
                )

            tests = self.ai_service.convert_to_objects(ai_data)

            return FinalOutput(
                tests=tests,
                summary=ai_data.get("summary", ""),
                explanations=ai_data.get("explanations", []),
                status=ProcessingStatus.OK
            )

        except Exception as e:
            return ErrorResponse(
                status=ProcessingStatus.ERROR,
                reason=f"Processing error: {str(e)}"
            )

    def process_image_input(self, image: Image.Image) -> Union[FinalOutput, ErrorResponse]:
        """Process image input (OCR → cleanup → single AI call)."""
        try:
            ocr_result = self.ocr_service.process_image_input(image)
            fixed_tests = self.ai_service.fix_ocr_errors(ocr_result.tests_raw)

            ai_data = self.ai_service.process_tests(fixed_tests)

            if not ai_data.get("validation", {}).get("is_valid", False):
                return ErrorResponse(
                    status=ProcessingStatus.UNPROCESSED,
                    reason=f"Validation failed: {ai_data['validation'].get('explanation', 'Unknown')}"
                )

            tests = self.ai_service.convert_to_objects(ai_data)

            return FinalOutput(
                tests=tests,
                summary=ai_data.get("summary", ""),
                explanations=ai_data.get("explanations", []),
                status=ProcessingStatus.OK
            )

        except Exception as e:
            return ErrorResponse(
                status=ProcessingStatus.ERROR,
                reason=f"Processing error: {str(e)}"
            )
            
    def get_step_by_step_results(self, text: str):
        """
        Run full pipeline step by step so demo endpoint can show results.
        """
        results = {}

        # Step 1: OCR Fix
        step1 = self.ai_service.fix_ocr_errors([text])
        results["step1_ocr"] = step1

        # Step 2–4: Normalize + Validation + Patient Summary
        step2_4 = self.ai_service.process_tests(step1)
        results["step2_normalization"] = step2_4.get("normalized_tests", [])
        results["step3_summary"] = {
            "summary": step2_4.get("summary", ""),
            "explanations": step2_4.get("explanations", [])
        }
        results["final_output"] = step2_4

        return results


# Global instance
processing_service = ProcessingService()
