# Production Dockerfile for Darukaa Biodiversity Intelligence AI
FROM python:3.13-slim

WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pypdf

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Run uvicorn server respecting PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
