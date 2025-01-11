FROM python:3.12-slim

WORKDIR /app

# Copy application files
COPY ../../app.py .
COPY ../../static ./static
COPY ../../templates ./templates
COPY ../../requirements.txt .
COPY ../../uber_llm_ocr.py .
COPY ../../uber_ocr_en.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Install system dependencies for reportlab and other packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make start script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
