# Use official Python slim image
FROM python:3.10-slim

# Install system dependencies needed by your app (Tesseract OCR, etc.)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose port 5000 to the outside world
EXPOSE 5000

# Run the Flask app with gunicorn, assuming your Flask app instance is "app" in run.py
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000"]
