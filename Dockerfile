# FastAPI application Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install fastapi uvicorn python-multipart jinja2 aiofiles

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
