@echo off
echo 🚀 Discord Music Bot Deployment Script
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file and add your DISCORD_TOKEN
    echo    Then run this script again.
    pause
    exit /b 1
)

REM Check if DISCORD_TOKEN is set
findstr /C:"DISCORD_TOKEN=" .env >nul
if errorlevel 1 (
    echo ❌ Please set your DISCORD_TOKEN in .env file
    pause
    exit /b 1
)

findstr /C:"your_discord_bot_token_here" .env >nul
if not errorlevel 1 (
    echo ❌ Please replace 'your_discord_bot_token_here' with your actual token
    pause
    exit /b 1
)

echo ✅ Environment check passed!

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully!

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg is not installed. Audio features may not work properly.
    echo    Please install FFmpeg from https://ffmpeg.org/download.html
    echo    and add it to your system PATH
)

echo.
echo 🎵 Starting Discord Music Bot...
echo Press Ctrl+C to stop the bot
echo.

REM Run the bot
python bot.py

pause 