#!/usr/bin/env bash
set -e

# Install runtime and testing dependencies
pip install --upgrade pip
pip install -r requirements.txt
# Install runtime dependencies
pip install -r requirements.txt

# Install test-specific dependencies
pip install pytest
