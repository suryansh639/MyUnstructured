#!/bin/bash
# Update script for Streamlit Document Processing App

echo "Stopping service..."
sudo systemctl stop streamlit-doc-processor.service

echo "Activating virtual environment..."
source streamlit_env/bin/activate

echo "Updating dependencies..."
pip install --upgrade -r requirements.txt

echo "Starting service..."
sudo systemctl start streamlit-doc-processor.service

echo "Update completed!"
