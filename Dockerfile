# Use official Python slim image
FROM python:3.10-slim

# Install system dependencies (Tesseract, OpenCV, and others)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    fonts-dejavu \
    libgl1 \                         # ✅ Fix for OpenCV ImportError (libGL.so.1)
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port
EXPOSE 5000

# Start the Flask app with gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000"]
