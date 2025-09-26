import logging
import google.generativeai as genai
import json
import re
from typing import List, Dict, Any
from app.models.schemas import (
    NormalizedTest, PatientFriendlySummary, ReferenceRange, TestStatus
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def safe_json_loads(text: str) -> Any:
    """
    Safely parse JSON from model output.
    Cleans common formatting issues before retrying.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip()

        # Remove leading/trailing markdown fences
        cleaned = re.sub(r"^```(json)?", "", cleaned, flags=re.MULTILINE).strip()
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        # Remove trailing commas
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

        # Ensure we capture only JSON object/array
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]

        try:
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"❌ Still invalid JSON after cleanup: {e}\nRaw: {text[:500]}")
            raise


class AIService:
    """AI service for medical test normalization, validation, and summarization."""

    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.temperature = settings.ai_temperature
        self.model = None

        try:
            if settings.gemini_api_key and settings.gemini_api_key.strip():
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("✅ AI Service initialized successfully")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not configured - AI features disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI service: {e}")
            self.model = None

    def fix_ocr_errors(self, texts: List[str]) -> List[str]:
        """Fix OCR errors in raw test strings."""
        try:
            if not texts or not self.model:
                return texts

            combined_text = " ".join(texts)
            prompt = f"""
You are a medical expert. Extract and clean medical test results from the following text.
Return ONLY a JSON array of individual test strings in the format:
["Hemoglobin 10.2 g/dL (Low)", "WBC 11200 /uL (High)"]

Rules:
1. Each test must have: TestName Value Unit (Status)
2. Remove headers like "CBC:", "LFT:", etc.
3. Fix OCR typos in test names and units
4. Standardize numbers (11200 not 11,200)
5. If nothing usable, return []

Return only valid JSON. Do not add extra text.

Input: "{combined_text}"
Output:
"""
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=400,
                ),
            )

            text_out = response.text.strip()
            return safe_json_loads(text_out)

        except Exception as e:
            logger.error(f"OCR fix failed: {e}")
            return texts

    def process_tests(self, original_tests: List[str]) -> Dict[str, Any]:
        """
        Single-prompt processing:
        - Normalize tests
        - Validate against hallucination
        - Generate patient-friendly summary
        """
        try:
            if not original_tests or not self.model:
                return {
                    "normalized_tests": [],
                    "validation": {"is_valid": False, "explanation": "No data"},
                    "summary": "Unable to analyze.",
                    "explanations": [],
                }

            input_text = "\n".join(original_tests)

            prompt = f"""
You are a medical AI assistant.
Process the following test results end-to-end.

Tasks:
1. Normalize each test into JSON with fields:
   {{
     "name": "standardized_test_name",
     "value": numeric_value,
     "unit": "standard_unit",
     "status": "normal|low|high|critical",
     "ref_range": {{"low": numeric_low, "high": numeric_high}}
   }}

2. Validate against the original text:
   - Ensure no extra tests are invented
   - Mark is_valid true/false, confidence score, issues_found[], explanation

3. Summarize for the patient:
   - One-sentence overall summary
   - Explanations for abnormal results (1–2 short sentences each)
   - Do not diagnose, only explain

Return ONLY valid JSON:
{{
  "normalized_tests": [...],
  "validation": {{
     "is_valid": true/false,
     "confidence_score": 0.0-1.0,
     "issues_found": [],
     "explanation": "..."
  }},
  "summary": "...",
  "explanations": ["...", "..."]
}}

Original Test Input:
{input_text}
"""
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=5000,
                ),
            )

            text_out = response.text.strip()
            return safe_json_loads(text_out)

        except Exception as e:
            logger.error(f"process_tests failed: {e}")
            return {
                "normalized_tests": [],
                "validation": {"is_valid": False, "explanation": str(e)},
                "summary": "Error processing results.",
                "explanations": [],
            }

    def convert_to_objects(self, ai_data: Dict[str, Any]) -> List[NormalizedTest]:
        """Convert AI JSON to NormalizedTest objects."""
        tests = []
        try:
            for t in ai_data.get("normalized_tests", []):
                status_map = {
                    "normal": TestStatus.NORMAL,
                    "low": TestStatus.LOW,
                    "high": TestStatus.HIGH,
                    "critical": TestStatus.CRITICAL,
                }
                status = status_map.get(t["status"].lower(), TestStatus.NORMAL)
                ref_range = ReferenceRange(
                    low=float(t["ref_range"]["low"]),
                    high=float(t["ref_range"]["high"]),
                )
                tests.append(
                    NormalizedTest(
                        name=t["name"],
                        value=float(t["value"]),
                        unit=t["unit"],
                        status=status,
                        ref_range=ref_range,
                    )
                )
        except Exception as e:
            logger.error(f"Conversion to objects failed: {e}")
        return tests
