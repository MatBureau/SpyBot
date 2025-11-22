#!/bin/bash
# Quick start script for Linux/Mac

echo "========================================"
echo "Amazon Price Monitor Bot"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found"
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[*] Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    playwright install-deps
    echo ""
    echo "[!] Please configure your .env file before running"
    echo "[!] Copy .env.example to .env and fill in your values"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[!] .env file not found"
    echo "[!] Copy .env.example to .env and configure your settings"
    exit 1
fi

# Run the bot
echo "[*] Starting Price Monitor Bot..."
echo ""
python main.py
