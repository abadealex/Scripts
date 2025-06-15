# Use slim Python base image to reduce size
FROM python:3.10-slim

# Install system dependencies needed for OpenCV, Tesseract OCR, and image rendering
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy only requirements file first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port Railway will use
EXPOSE 8000

# Start the app using Gunicorn and wsgi.py (which should contain: app = create_app())
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]
