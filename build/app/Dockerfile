FROM python:3.12-slim

WORKDIR /app

# Copy application files
COPY ./app/app.py ./app/
COPY ../../static ./static
COPY ../../templates ./templates
COPY ../../requirements.txt .
COPY ../../uber_llm_ocr.py ./app/
COPY ../../uber_ocr_en.py ./app/
COPY start.sh .

# Ensure correct Python path
ENV PYTHONPATH=/app

# Install system dependencies for reportlab and other packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make start script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Use uvicorn directly
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
