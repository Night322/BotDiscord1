# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### Added
- 🎵 **Multi-server support** - Separate queues for each Discord server
- 🔁 **Loop mode** - Toggle loop for continuous playback
- 🗑️ **Remove songs** - Remove songs from queue by position
- 🎛️ **Interactive buttons** - Button-based controls for easy access
- 📊 **Rich embeds** - Beautiful, informative messages with song details
- 🛡️ **Better error handling** - Comprehensive error messages and logging
- 📱 **Railway deployment** - Easy deployment on Railway platform
- 🚀 **Deployment scripts** - Automated setup scripts for Windows/Linux

### Changed
- 🔄 **Improved queue system** - Better queue management with MusicQueue class
- 🎧 **Enhanced audio quality** - Better FFmpeg configuration and audio processing
- 📝 **Better logging** - Structured logging with different levels
- 🏗️ **Code structure** - Improved code organization and type hints

### Fixed
- 🐛 **Queue access errors** - Fixed linter errors with proper queue access
- 🔧 **Environment variables** - Better handling of missing tokens
- 🎵 **Audio playback** - Improved error handling for audio issues
- ⏱️ **Timeout handling** - Better timeout management for YouTube downloads

## [1.0.0] - 2024-01-XX

### Added
- 🎵 **Basic music playback** - Play music from YouTube URLs and search
- 📜 **Queue system** - Add songs to queue and play sequentially
- ⏯️ **Playback controls** - Play, pause, resume, skip, stop
- 🎧 **Voice channel support** - Join and leave voice channels
- 📱 **Slash commands** - Modern Discord slash command interface
- 🎛️ **Basic controls** - Simple button controls for playback

### Features
- YouTube music playback
- Basic queue management
- Voice channel integration
- Slash command support
- Auto-disconnect when no one is listening 