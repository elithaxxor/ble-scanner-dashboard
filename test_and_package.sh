#!/bin/bash

echo "🧪 Starting BLE Scanner Test Suite..."
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo -e "\n📦 Installing requirements..."
pip install -r requirements.txt

# Initialize database
echo -e "\n💾 Initializing database..."
python create_db.py

# Run notification tests
echo -e "\n🔔 Testing notification system..."
python test_notifications.py

# Run BLE scanner tests
echo -e "\n🔍 Testing BLE scanner..."
python test_ble_scanner.py

# Create distribution package
echo -e "\n📦 Creating distribution package..."
mkdir -p dist
zip -r dist/ble-scanner.zip \
    *.py \
    requirements.txt \
    .env.example \
    .gitignore \
    README.md \
    templates/ \
    --exclude "*__pycache__*" \
    --exclude "*.pyc" \
    --exclude "*.log" \
    --exclude "*.db"

echo -e "\n✅ Test and packaging complete!"
echo "Distribution package created at: dist/ble-scanner.zip"
echo "====================================="

# Deactivate virtual environment
deactivate
