#!/bin/bash
set -e
trap 'echo "❌ Local dev environment setup failed."' ERR

echo ""
echo "📦 Installing pre-commit hook dependencies..."
npm install
echo "✅ Done."

echo ""
echo "🐍 Setting up and activating Python virtual environment..."
[ ! -d ".venv" ] && python3 -m venv .venv
source .venv/bin/activate
echo "✅ Done."

echo ""
echo "⬆️  Upgrading pip and installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Done."

echo ""
echo "🎉 Setup complete."
echo "🐘 See ./sql for SQL files to set up and populate your database."
echo ""