#!/bin/bash
set -e

echo "Starting application with uvicorn..."
cd /app
exec uvicorn app.app:app --host 0.0.0.0 --port 8000
