#!/bin/bash

# SmartWealthAI Virtual Environment Activation Script
echo "Activating SmartWealthAI virtual environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies if requirements.txt exists
if [ -f "SmartWealthSimple/app/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r SmartWealthSimple/app/requirements.txt
fi

echo "Virtual environment activated successfully!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "To deactivate, run: deactivate"
echo "To install new packages: pip install <package_name>"
