# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libmagic-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements-docker.txt requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Test that the application can import and start
RUN python startup_test.py

# Expose port
EXPOSE 8000

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Command to run the application with startup validation and better logging
CMD ["sh", "-c", "echo 'Starting Medical Report Simplifier on port ${PORT:-8000}...' && python startup_test.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info --access-log"]
