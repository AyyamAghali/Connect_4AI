#!/bin/bash

# Connect 4 AI - Startup Script for macOS/Linux

echo "=========================================="
echo "  Connect 4 AI Game - Starting Server"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "Starting Flask server..."
echo "Server will be available at: http://localhost:5001"
echo "Open index.html in your browser to play!"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start the Flask server
python3 app.py
