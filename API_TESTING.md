# Medical Report Simplifier - API Testing Guide

## Replace YOUR_RAILWAY_URL with your actual Railway app URL

# 1. Health Check
curl -X GET "https://YOUR_RAILWAY_URL/api/v1/health"

# 2. Root endpoint
curl -X GET "https://YOUR_RAILWAY_URL/"

# 3. Process text input
curl -X POST "https://YOUR_RAILWAY_URL/api/v1/process-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Blood Test Results: Hemoglobin: 12.5 g/dL (Normal: 12-16), Glucose: 95 mg/dL (Normal: 70-100)"
  }'

# 4. Process image (replace with actual image file path)
curl -X POST "https://YOUR_RAILWAY_URL/api/v1/process-image" \
  -F "file=@/path/to/your/medical-report.jpg"

# 5. Debug text processing steps
curl -X POST "https://YOUR_RAILWAY_URL/api/v1/debug-steps" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "CBC: WBC 7500, RBC 4.2M, Hemoglobin 13.8"
  }'

# 6. View API documentation in browser
# Open: https://YOUR_RAILWAY_URL/docs
