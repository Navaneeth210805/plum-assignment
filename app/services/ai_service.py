import logging
import google.generativeai as genai
import json
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import NormalizedTest, PatientFriendlySummary, ReferenceRange, TestStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered explanations and medical data processing using Google Gemini"""
    
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.temperature = settings.ai_temperature
        self.model = None
        
        # Initialize AI service if API key is available
        try:
            if settings.gemini_api_key and settings.gemini_api_key.strip():
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("✅ AI Service initialized successfully")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not configured - AI features will be limited")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI service: {e}")
            self.model = None
    
    def generate_patient_summary(self, tests: List[NormalizedTest]) -> PatientFriendlySummary:
        """Generate patient-friendly summary using Gemini AI"""
        try:
            if not tests:
                return PatientFriendlySummary(
                    summary="No test results found to analyze.",
                    explanations=[]
                )
            
            # Check if AI model is available
            if not self.model:
                return PatientFriendlySummary(
                    summary="AI service unavailable. Please configure GEMINI_API_KEY.",
                    explanations=[]
                )
            
            # Create prompt for AI
            prompt = self._create_summary_prompt(tests)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=800,
                )
            )
            
            # Parse response
            summary_data = self._parse_ai_response(response.text)
            
            summary = summary_data.get('summary', 'Analysis completed.')
            explanations = summary_data.get('explanations', [])
            print(summary)
            print(explanations)
            
            return PatientFriendlySummary(
                summary=summary_data.get('summary', 'Analysis completed.'),
                explanations=summary_data.get('explanations', [])
            )
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {str(e)}")
            return PatientFriendlySummary(
                summary="Unable to generate summary at this time.",
                explanations=[]
            )
    
    def validate_against_hallucination(self, original_tests: List[str], 
                                           normalized_tests: List[NormalizedTest]) -> Tuple[bool, str]:
        """
        Use AI to validate that normalized tests don't contain hallucinated information
        by comparing semantic context between original and normalized data
        """
        try:
            if not original_tests or not normalized_tests:
                return False, "No data to validate"
            
            # Prepare original text
            original_text = ' '.join(original_tests)
            
            # Prepare normalized test summary
            normalized_summary = []
            for test in normalized_tests:
                test_info = f"{test.name}: {test.value} {test.unit} ({test.status})"
                normalized_summary.append(test_info)
            normalized_text = ', '.join(normalized_summary)
            
            # Create AI validation prompt
            prompt = f"""
You are a medical expert validator. Compare the original medical test data with the normalized results to detect hallucinations or fabricated information.

ORIGINAL TEXT:
{original_text}

NORMALIZED RESULTS:
{normalized_text}

Your task:
1. Check if all normalized test names correspond to tests mentioned in the original text
2. Verify that values and units in normalized results match the original data
3. Ensure no completely new tests were invented/hallucinated
4. Allow for reasonable standardization (e.g., "Hgb" -> "Hemoglobin", unit conversions)

Respond with ONLY a JSON object:
{{
    "is_valid": true/false,
    "confidence_score": 0.0-1.0,
    "issues_found": ["list of specific issues if any"],
    "explanation": "brief explanation of validation result"
}}

If the normalized results accurately represent the original data (allowing for medical standardization), return is_valid: true.
If there are fabricated tests, wrong values, or significant discrepancies, return is_valid: false.
"""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent validation
                    max_output_tokens=400,
                )
            )
            
            # Parse AI response
            response_text = response.text.strip()
            
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                validation_result = json.loads(json_str)
                
                is_valid = validation_result.get('is_valid', False)
                confidence = validation_result.get('confidence_score', 0.0)
                issues = validation_result.get('issues_found', [])
                explanation = validation_result.get('explanation', 'No explanation provided')
                
                # Apply configurable confidence threshold
                settings = get_settings()
                threshold = settings.validation_confidence_threshold
                
                if confidence < threshold:
                    logger.warning(f"Low validation confidence: {confidence} (threshold: {threshold})")
                    return False, f"Low confidence validation ({confidence:.2f}): {explanation}"
                
                if not is_valid:
                    issue_text = '; '.join(issues) if issues else explanation
                    logger.warning(f"Validation failed: {issue_text}")
                    return False, issue_text
                
                logger.info(f"Validation passed with confidence {confidence:.2f}")
                return True, "Validation passed"
            
            # Fallback if JSON parsing fails
            logger.error("Failed to parse AI validation response")
            return False, "Failed to parse validation response"
            
        except Exception as e:
            logger.error(f"Hallucination validation failed: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def normalize_test_with_ai(self, test_string: str) -> Optional[Dict[str, Any]]:
        """Use AI to normalize a single test result"""
        try:
            prompt = f"""
You are a medical AI assistant. Parse this medical test result and return ONLY a JSON object with the normalized information.

Input: "{test_string}"

Return a JSON object with this exact structure:
{{
    "name": "standardized_test_name",
    "value": numeric_value,
    "unit": "standard_unit",
    "status": "normal|low|high|critical",
    "ref_range": {{"low": numeric_low, "high": numeric_high}}
}}

Rules:
1. Standardize test names (e.g., "Hgb" -> "Hemoglobin", "WBC" -> "White Blood Cell Count")
2. Convert units to standard format (g/dL, /uL, mg/dL, etc.)
3. Use standard reference ranges for adults
4. Status should be based on the reference range
5. Return ONLY the JSON object, no other text
6. If you cannot parse the test, return null

"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                )
            )
            
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            if response_text.lower() == 'null':
                return None
                
            # Find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Validate the structure
                required_fields = ['name', 'value', 'unit', 'status', 'ref_range']
                if all(field in parsed_data for field in required_fields):
                    return parsed_data
            
            return None
            
        except Exception as e:
            logger.error(f"AI normalization failed for '{test_string}': {str(e)}")
            return None
    
    def create_normalized_test_from_ai(self, ai_data: Dict[str, Any]) -> Optional[NormalizedTest]:
        """Convert AI response to NormalizedTest object"""
        try:
            # Map status string to enum
            status_map = {
                'normal': TestStatus.NORMAL,
                'low': TestStatus.LOW,
                'high': TestStatus.HIGH,
                'critical': TestStatus.CRITICAL
            }
            
            status = status_map.get(ai_data['status'].lower(), TestStatus.NORMAL)
            
            ref_range = ReferenceRange(
                low=float(ai_data['ref_range']['low']),
                high=float(ai_data['ref_range']['high'])
            )
            
            return NormalizedTest(
                name=ai_data['name'],
                value=float(ai_data['value']),
                unit=ai_data['unit'],
                status=status,
                ref_range=ref_range
            )
            
        except Exception as e:
            logger.error(f"Failed to create NormalizedTest from AI data: {str(e)}")
            return None
    
    def _create_summary_prompt(self, tests: List[NormalizedTest]) -> str:
        """Create prompt for AI summary generation"""
        test_descriptions = []
        
        for test in tests:
            status_desc = "normal" if test.status == "normal" else f"{test.status} ({test.value} {test.unit})"
            test_descriptions.append(f"- {test.name}: {status_desc}")
        
        prompt = f"""
You are a medical assistant helping patients understand their lab results. 
Analyze the following test results and provide a patient-friendly explanation.

IMPORTANT RULES:
1. Do NOT diagnose or suggest medical conditions
2. Only explain what the tests show, not what they might mean medically
3. Use simple, non-technical language
4. Be reassuring but factual
5. Always recommend consulting with a healthcare provider
6. Do NOT add any test results that aren't listed below
7. Always give explanations for any abnormal (low/high/critical) results no matter how minor it is. But explanations should be brief (1-2 sentences each) and general.

Test Results:
{chr(10).join(test_descriptions)}

Please provide:
1. A brief summary (1-2 sentences) of the overall findings and give common explanations if found lows or highs in any area.

Example format:
"summary" : "Low hemoglobin and high white blood cell count."
"explanations": [
    "Low hemoglobin may indicate anemia","High WBC can occur with infections."]

Format your response as follows:
SUMMARY: [brief overall summary]
EXPLANATIONS: [explanation for abnormal result 1, explanation for abnormal result 2].

"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            lines = response_text.strip().split('\n')
            print(lines)
            summary = ""
            explanations = []
            
            current_section = None
            
            # handle explanations properly as per the format
            for line in lines:
                line = line.strip()
                if "SUMMARY" in line:
                    current_section = "summary"
                    summary = line[len("SUMMARY:"):].strip()
                elif "EXPLANATIONS" in line:
                    current_section = "explanations"
                elif current_section == "explanations" and line:
                    line = line[1:].strip()
                    explanations.append(line)
            
            # Clean up summary
            print(summary)
            print(explanations)
            explanations = [exp.strip() for exp in explanations if exp]
            summary = summary.strip()
            if not summary:
                summary = "Test results have been analyzed."
            if not explanations:
                explanations = ["No explanations available."]
            return {
                'summary': summary,
                'explanations': explanations
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return {
                'summary': "Analysis completed.",
                'explanations': []
            }
    
    def fix_ocr_errors(self, texts: List[str]) -> List[str]:
        try:
            if not texts:
                return texts
            
            combined_text = " ".join(texts)
            
            prompt = f"""
You are a medical expert. Extract and clean medical test results from the following text. 
Return ONLY a JSON array of individual test strings.

Rules:
1. Each test should have: TestName Value Unit (Status) format
2. Remove headers like "CBC:", "Complete Blood Count:", etc.
3. Fix common OCR errors and typos
4. Standardize numbers (remove commas: 11,200 -> 11200).
5. Fix minor typos in test names (e.g., "Hemoglogin" -> "Hemoglobin")

Example:
Input: "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
Output: ["Hemoglobin 10.2 g/dL (Low)", "WBC 11200 /uL (High)"]

Input: "{combined_text}"

Output:
"""
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            response_text = response.text.strip()
            
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed_list = json.loads(json_str)
                    if isinstance(parsed_list, list):
                        return parsed_list
                    else:
                        return texts
                else:
                    return texts

            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON for combined text")
                return texts

        except Exception as e:
            logger.error(f"OCR error fixing failed: {str(e)}")
            return texts
