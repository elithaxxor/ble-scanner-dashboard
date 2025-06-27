#!/bin/bash
set -e

PYTHON=python3
case "$(uname)" in
    Darwin*) PYTHON=python3 ;;
    Linux*) PYTHON=python3 ;;
esac

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  $PYTHON -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Launch the scanner in the background (creates DB on first run)
$PYTHON sniff_my_ble.py --interval 5 --workers 1 &

# Start the FastAPI dashboard
$PYTHON -m api

