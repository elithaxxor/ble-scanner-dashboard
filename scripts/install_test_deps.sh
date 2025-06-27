#!/usr/bin/env bash
set -e

# Install runtime and testing dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
