#!/bin/bash

set -e

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Initialize the database (run once, safe to repeat)
python main.py

# Start the web dashboard
python web_app.py
