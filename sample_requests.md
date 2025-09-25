# Medical Report Simplifier - Sample API Requests

## 1. Health Check
curl -X GET "http://localhost:8000/api/v1/health"

## 2. Process Text Input - Normal Case
curl -X POST "http://localhost:8000/api/v1/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
  }'

## 3. Process Text Input - Multiple Tests
curl -X POST "http://localhost:8000/api/v1/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Complete Blood Count Results: Hemoglobin 8.5 g/dL (Low), WBC 15000 /uL (High), RBC 3.2 million/uL (Low), Platelet 450000 /uL (Normal)"
  }'

## 4. Process Text Input - OCR-like with Errors
curl -X POST "http://localhost:8000/api/v1/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "CBC: Hemglobin 10.2 g/dL (Low), WBC 11200 /uL (Hgh)"
  }'

## 5. Process Text Input - No Medical Tests (Should fail)
curl -X POST "http://localhost:8000/api/v1/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is just regular text without any medical information."
  }'

## 6. Process Image Input (replace with actual image file)
curl -X POST "http://localhost:8000/api/v1/process-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_medical_report.png"

## 7. Debug Processing Steps - Text
curl -X POST "http://localhost:8000/api/v1/debug-steps" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
  }'

## 8. Debug Processing Steps - Image
curl -X POST "http://localhost:8000/api/v1/debug-steps-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_medical_report.png"

## 9. Demo Problem Statement Format - Shows exact format from assignment
curl -X POST "http://localhost:8000/api/v1/demo-problem-statement" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "CBC: Hemglobin 10.2 g/dL (Low), WBC 11,200 /uL (Hgh)"
  }'

## Expected Success Response Format:
## {
##   "tests": [
##     {
##       "name": "Hemoglobin",
##       "value": 10.2,
##       "unit": "g/dL",
##       "status": "low",
##       "ref_range": {"low": 12.0, "high": 15.0}
##     },
##     {
##       "name": "WBC",
##       "value": 11200,
##       "unit": "/uL",
##       "status": "high",
##       "ref_range": {"low": 4000, "high": 11000}
##     }
##   ],
##   "summary": "Low hemoglobin and high white blood cell count detected.",
##   "status": "ok"
## }

## Expected Error Response Format:
## {
##   "status": "unprocessed",
##   "reason": "No medical tests found in input text"
## }
