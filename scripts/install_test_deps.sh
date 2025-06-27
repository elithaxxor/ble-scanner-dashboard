#!/usr/bin/env bash
set -e

# Install runtime dependencies
pip install -r requirements.txt

# Install test-specific dependencies
pip install pytest
