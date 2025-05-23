#!/bin/bash

# Make sure Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first: pip install poetry==2.1.3"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Run the FastAPI application
echo "Starting the FastAPI application..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 