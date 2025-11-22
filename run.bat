@echo off
REM Quick start script for Windows

echo ========================================
echo Amazon Price Monitor Bot
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [!] Virtual environment not found
    echo [*] Creating virtual environment...
    python -m venv venv
    echo [*] Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    playwright install chromium
    echo.
    echo [!] Please configure your .env file before running
    echo [!] Copy .env.example to .env and fill in your values
    pause
    exit
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo [!] .env file not found
    echo [!] Copy .env.example to .env and configure your settings
    pause
    exit
)

REM Run the bot
echo [*] Starting Price Monitor Bot...
echo.
python main.py
