#!/bin/bash

echo "🚀 Discord Music Bot Deployment Script"
echo "======================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your DISCORD_TOKEN"
    echo "   Then run this script again."
    exit 1
fi

# Check if DISCORD_TOKEN is set
if ! grep -q "DISCORD_TOKEN=" .env || grep -q "your_discord_bot_token_here" .env; then
    echo "❌ Please set your DISCORD_TOKEN in .env file"
    exit 1
fi

echo "✅ Environment check passed!"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Audio features may not work properly."
    echo "   Please install FFmpeg:"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
fi

echo ""
echo "🎵 Starting Discord Music Bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python3 bot.py 