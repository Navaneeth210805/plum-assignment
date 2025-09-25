import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Medical Report Simplifier API" in data["message"]


def test_process_text_valid_input():
    """Test text processing with valid input"""
    test_data = {
        "text": "CBC: Hemoglobin 10.2 g/dL (Low), WBC 11,200 /uL (High)"
    }
    
    response = client.post("/api/v1/process-text", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "tests" in data
    assert "summary" in data
    assert data["status"] == "ok"


def test_process_text_empty_input():
    """Test text processing with empty input"""
    test_data = {"text": ""}
    
    response = client.post("/api/v1/process-text", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "unprocessed"


def test_process_text_invalid_input():
    """Test text processing with invalid input"""
    test_data = {"text": "This is not a medical report"}
    
    response = client.post("/api/v1/process-text", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "unprocessed"


def test_process_image_no_file():
    """Test image processing without file"""
    response = client.post("/api/v1/process-image")
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__])
