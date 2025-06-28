# Discord Music Bot 🎵

A feature-rich Discord music bot built with discord.py that supports YouTube music playback.

## Features ✨

- 🎶 **Music Playback**: Play music from YouTube URLs or search terms
- 📜 **Queue Management**: Add, remove, and view songs in queue
- 🔁 **Loop Mode**: Toggle loop for continuous playback
- ⏯️ **Playback Controls**: Play, pause, resume, skip, and stop
- 🎛️ **Interactive Controls**: Button-based controls for easy access
- 👥 **Multi-Server Support**: Separate queues for each Discord server
- 🎧 **Auto-Disconnect**: Automatically leaves when no one is listening
- 📱 **Slash Commands**: Modern Discord slash command interface

## Commands 📋

| Command | Description |
|---------|-------------|
| `/play [url/search]` | Play a song from YouTube or search |
| `/skip` | Skip the current song |
| `/stop` | Stop music and clear queue |
| `/pause` | Pause the current song |
| `/resume` | Resume paused music |
| `/queue` | View the current queue |
| `/remove [position]` | Remove a song from queue |
| `/loop` | Toggle loop mode |
| `/leave` | Disconnect from voice channel |
| `/help` | Show help information |

## 🚀 Deploy on Railway (Recommended)

### Step 1: Fork this Repository
1. Click the "Fork" button at the top right of this page
2. This will create a copy in your GitHub account

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Click "Deploy Now"

### Step 3: Set Environment Variables
1. In your Railway project, go to "Variables" tab
2. Add the following variable:
   - **Name**: `DISCORD_TOKEN`
   - **Value**: Your Discord bot token

### Step 4: Get Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Enable these permissions:
   - Send Messages
   - Use Slash Commands
   - Connect
   - Speak
   - Use Voice Activity

### Step 5: Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select the permissions mentioned above
4. Copy the generated URL and open it
5. Select your server and authorize

## 🛠️ Local Setup

### Prerequisites
1. **Python 3.8+** installed
2. **FFmpeg** installed and in PATH
3. **Discord Bot Token**

### Installation
1. **Clone repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**
   ```bash
   cp env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

4. **Install FFmpeg**
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`

5. **Run the bot**
   ```bash
   python bot.py
   ```

## 📁 Project Structure

```
discord-music-bot/
├── bot.py              # Main bot file
├── requirements.txt     # Python dependencies
├── Procfile            # For Railway
├── runtime.txt         # Python version
├── setup.py            # Package setup
├── .dockerignore       # Docker ignore rules
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── env.example         # Environment variables example
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes |

### Bot Permissions
Make sure your bot has these permissions:
- **Send Messages**
- **Use Slash Commands**
- **Connect** (Voice)
- **Speak** (Voice)
- **Use Voice Activity**

## 🎯 Usage Examples

### Playing Music
```
/play despacito
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Queue Management
```
/queue                    # View current queue
/remove 3                 # Remove 3rd song from queue
/loop                     # Toggle loop mode
```

### Playback Control
```
/pause                    # Pause current song
/resume                   # Resume paused song
/skip                     # Skip to next song
/stop                     # Stop and clear queue
```

## 🚨 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Install FFmpeg and ensure it's in PATH
   - Restart terminal after installation

2. **"Bot can't join voice channel"**
   - Check bot permissions in Discord server
   - Ensure bot has "Connect" and "Speak" permissions

3. **"No audio playing"**
   - Check if you're in the same voice channel as bot
   - Verify system audio is working

4. **"Commands not working"**
   - Ensure bot has "Use Slash Commands" permission
   - Wait for commands to sync (up to 1 hour)

### Railway Specific Issues

1. **Build fails**
   - Check Railway logs for error messages
   - Ensure all files are committed to GitHub

2. **Bot not responding**
   - Check if `DISCORD_TOKEN` is set correctly
   - Verify bot is online in Discord

3. **Audio issues on Railway**
   - Railway may have limitations with audio processing
   - Consider using a VPS for better audio performance

## 📊 Monitoring

### Railway Dashboard
- View real-time logs
- Monitor resource usage
- Check deployment status

### Bot Status
- Bot will show "Online" in Discord when running
- Use `/help` to test if commands are working

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you need help:
1. Check the troubleshooting section
2. Review Railway logs
3. Create an issue in the repository

---

**🎵 Enjoy your music bot!** 