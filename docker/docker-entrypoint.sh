#!/bin/bash

# Start the FastAPI application with the scheduler
echo "Starting Stock API with scheduler..."

# Set the Python path
export PYTHONPATH=/app

# Start the uvicorn server
exec uvicorn app.api:app --host 0.0.0.0 --port 8000
