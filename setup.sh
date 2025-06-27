#!/bin/bash
set -e

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Launch the scanner in the background (creates DB on first run)
python sniff_my_ble.py --interval 5 --workers 1 &

# Start the FastAPI dashboard
python -m api

