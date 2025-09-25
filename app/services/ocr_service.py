import pytesseract
import re
from PIL import Image
from typing import List, Tuple
from fuzzywuzzy import fuzz
from app.models.schemas import OCRResult
from app.core.config import get_settings

settings = get_settings()


class OCRService:
    def __init__(self):
        # Set tesseract command path if specified
        if hasattr(settings, 'tesseract_cmd') and settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    
    def extract_text_from_image(self, image: Image.Image) -> Tuple[str, float]:
        """Extract text from image using OCR"""
        try:
            # Get OCR data with confidence scores
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 0:  # Only include words with confidence > 0
                    word = ocr_data['text'][i].strip()
                    if word:
                        text_parts.append(word)
                        confidences.append(int(conf))
            
            extracted_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return extracted_text, avg_confidence / 100.0  # Convert to 0-1 scale
            
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return "", 0.0
    
    
    def fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors in medical text"""
        
        # Common OCR corrections for medical terms
        corrections = {
            # Test names
            r'\bHemglobin\b': 'Hemoglobin',
            r'\bHemoglobinn\b': 'Hemoglobin',
            r'\bHgb\b': 'Hemoglobin',
            r'\bWBC\b': 'WBC',
            r'\bRBC\b': 'RBC',
            
            # Status corrections
            r'\bHgh\b': 'High',
            r'\bLow\b': 'Low',
            r'\bNormal\b': 'Normal',
            r'\bHigh\b': 'High',
            
            # Unit corrections
            r'/uL\b': '/uL',
            r'/ul\b': '/uL',
            r'\bg/dL\b': 'g/dL',
            r'\bg/dl\b': 'g/dL',
            r'\bmg/dL\b': 'mg/dL',
            r'\bmg/dl\b': 'mg/dL',
            
            # Number corrections
            r'\bO\b': '0',  # O -> 0
            r'\bl\b': '1',  # l -> 1
            r'\bI\b': '1',  # I -> 1
        }
        
        corrected_text = text
        for pattern, replacement in corrections.items():
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text
    
    def extract_medical_tests(self, text: str) -> List[str]:
        """Extract medical test information from text"""
        # Clean the text first
        cleaned_text = self.fix_common_ocr_errors(text)
        
        # Pattern to match medical test results
        # Matches: TestName Number Unit (Status) or TestName: Number Unit (Status)
        test_patterns = [
            r'([A-Za-z\s]+)[:]\s*([0-9,]+\.?[0-9]*)\s*([a-zA-Z/μ%]+)\s*\(([A-Za-z]+)\)',
            r'([A-Za-z\s]+)\s+([0-9,]+\.?[0-9]*)\s*([a-zA-Z/μ%]+)\s*\(([A-Za-z]+)\)',
            r'([A-Za-z\s]+)[:]\s*([0-9,]+\.?[0-9]*)\s*([a-zA-Z/μ%]+)',
            r'([A-Za-z\s]+)\s+([0-9,]+\.?[0-9]*)\s*([a-zA-Z/μ%]+)'
        ]
        
        tests = []
        lines = cleaned_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in test_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if len(match) >= 3:
                        test_name = match[0].strip()
                        value = match[1].replace(',', '')  # Remove commas from numbers
                        unit = match[2].strip()
                        status = match[3].strip() if len(match) > 3 else ""
                        
                        # Format the test result
                        if status:
                            test_result = f"{test_name} {value} {unit} ({status})"
                        else:
                            test_result = f"{test_name} {value} {unit}"
                        
                        tests.append(test_result)
        
        # Remove duplicates while preserving order
        unique_tests = []
        seen = set()
        for test in tests:
            if test.lower() not in seen:
                unique_tests.append(test)
                seen.add(test.lower())
        
        return unique_tests
        
    
    def process_text_input(self, text: str) -> OCRResult:
        """Process direct text input"""
        # Apply OCR error corrections even for direct text
        # cleaned_text = self.fix_common_ocr_errors(text)
        
        # Extract tests from cleaned text
        # tests = self.extract_medical_tests(cleaned_text)
        
        # High confidence for direct text input
        confidence = 0.95 if text else 0.5
        print(text)
        
        return OCRResult(
            tests_raw=[text],
            confidence=confidence
        )
    
    def process_image_input(self, image: Image.Image) -> OCRResult:
        """Process image input with OCR"""
        # Extract text using OCR
        extracted_text, ocr_confidence = self.extract_text_from_image(image)
        print(extracted_text)
        
        if not extracted_text.strip():
            return OCRResult(tests_raw=[], confidence=0.0)
        
        final_confidence = ocr_confidence
        
        return OCRResult(
            tests_raw=[extracted_text],
            confidence=final_confidence
        )


# Global instance
ocr_service = OCRService()
