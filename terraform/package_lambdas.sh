#!/bin/bash
set -e

echo "📦 Packaging Lambda Functions..."

cd lambda_functions

# Package register_user
echo "Packaging register_user..."
cp register_user.py index.py
zip register_user.zip index.py
rm index.py

# Package get_credits
echo "Packaging get_credits..."
cp get_credits.py index.py
zip get_credits.zip index.py
rm index.py

# Package process_document
echo "Packaging process_document..."
cp process_document.py index.py
zip process_document.zip index.py
rm index.py

echo "✅ All Lambda functions packaged!"
ls -lh *.zip
