#!/bin/bash

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found in root. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing/Updating dependencies..."
pip install -r backend/requirements.txt

# Run the application
echo "Starting Tally Agent Backend..."
cd backend
python3 main.py
