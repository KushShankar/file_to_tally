#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "=========================================="
echo "     Excel to Tally AI Agent Launcher"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3 using your package manager (e.g., sudo apt install python3)"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for virtual environment
if [ -d ".venv" ] && [ ! -f ".venv/bin/activate" ]; then
    echo "[WARN] Invalid virtual environment detected. Recreating..."
    rm -rf .venv
fi

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo "[INFO] Activating environment..."
source .venv/bin/activate

# Update pip
echo "[INFO] Checking dependencies..."
python3 -m pip install --upgrade pip > /dev/null

# Install dependencies
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    read -p "Press Enter to exit..."
    exit 1
fi

# Run the application
echo ""
echo "[INFO] Starting application..."
python3 start_app.py

# Keep window open if there was an error
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application stopped unexpectedly."
    read -p "Press Enter to exit..."
fi
