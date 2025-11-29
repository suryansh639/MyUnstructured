#!/bin/bash

set -e

echo "Updating system..."
sudo apt update -y

echo "Installing Unstructured dependencies..."
sudo apt install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmagic1 \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    python3-dev

echo "Setup completed successfully!"
