#!/bin/bash

echo "Setting up pre-commit hooks..."
npm install

echo "Verifying or setting up Python virtual environment..."
[ ! -d ".venv" ] && python3 -m venv .venv

echo "Activating Python virtual environment..."
source .venv/bin/activate

echo "Upgrading pip and installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete."