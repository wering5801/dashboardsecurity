# Falcon Security Dashboard - Dockerfile for Google Cloud Run
# Optimized for production deployment

# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY security-dashboard/ ./security-dashboard/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port for Cloud Run
EXPOSE 8080

# Health check (optional but recommended)
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run the application
CMD streamlit run security-dashboard/app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true \
    --browser.gatherUsageStats=false
