import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp as youtube_dl
import asyncio
import logging
from typing import Optional, List
import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    print("❌ DISCORD_TOKEN not found in environment variables")
    print("Please set DISCORD_TOKEN in Railway Variables")
    exit(1)

# YouTube DL configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'extractaudio': True,
    'audioformat': 'mp3',
    'prefer_ffmpeg': True,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 192k'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'Unknown')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader', 'Unknown')
        self.duration = data.get('duration', 0)
        self.webpage_url = data.get('webpage_url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, timeout=30):
        loop = loop or asyncio.get_event_loop()

        def extract():
            try:
                return ytdl.extract_info(url, download=not stream)
            except Exception as e:
                logger.error(f"Error extracting info: {str(e)}")
                raise Exception(f"Error extracting info: {str(e)}")

        try:
            data = await asyncio.wait_for(loop.run_in_executor(None, extract), timeout)
        except asyncio.TimeoutError:
            raise Exception("⏱️ Timeout while fetching media. Please try another song or check your connection.")
        except Exception as e:
            raise Exception(f"❌ Error: {str(e)}")

        if not data:
            raise Exception("❌ Could not find any audio to play.")

        if 'entries' in data:
            if len(data['entries']) == 0:
                raise Exception("❌ No playable entries found.")
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        try:
            return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        except Exception as e:
            raise Exception(f"❌ FFmpeg error: {str(e)}")

    def format_duration(self):
        """Format duration to MM:SS"""
        if self.duration and self.duration > 0:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes}:{seconds:02d}"
        return "Unknown"

class MusicQueue:
    def __init__(self):
        self.queue: List[YTDLSource] = []
        self.current: Optional[YTDLSource] = None
        self.loop = False
        self.shuffle = False

    def add(self, item: YTDLSource):
        self.queue.append(item)

    def remove(self, index: int) -> Optional[YTDLSource]:
        if 0 <= index < len(self.queue):
            return self.queue.pop(index)
        return None

    def clear(self):
        self.queue.clear()
        self.current = None

    def get_next(self) -> Optional[YTDLSource]:
        if not self.queue:
            return None
        return self.queue.pop(0)

    def __len__(self):
        return len(self.queue)

    def __getitem__(self, index):
        return self.queue[index]

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}  # Store queues per guild
        self.leave_check.start()

    def get_queue(self, guild_id: int) -> MusicQueue:
        """Get or create music queue for a guild"""
        if guild_id not in self.music_queues:
            self.music_queues[guild_id] = MusicQueue()
        return self.music_queues[guild_id]

    @app_commands.command(name="play", description="🎶 Play music from a URL or search term")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        user = interaction.user
        guild = interaction.guild
        if not guild or not isinstance(user, discord.Member) or not user.voice or not user.voice.channel:
            return await interaction.followup.send(embed=self._make_embed("❗ You must be in a voice channel to use this command.", discord.Color.red()))

        vc = guild.voice_client if guild else None
        if not vc:
            try:
                await user.voice.channel.connect()
            except Exception as e:
                logger.error(f"Failed to connect to voice channel: {e}")
                return await interaction.followup.send(embed=self._make_embed(f"❌ Failed to connect to voice channel: {str(e)}", discord.Color.red()))
        elif vc.channel != user.voice.channel:
            return await interaction.followup.send(embed=self._make_embed("❗ You must be in the same voice channel as the bot.", discord.Color.red()))

        try:
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
        except Exception as e:
            return await interaction.followup.send(embed=self._make_embed(str(e), discord.Color.red()))

        vc = guild.voice_client if guild else None
        queue = self.get_queue(guild.id) if guild else None
        if vc and isinstance(vc, discord.VoiceClient) and (vc.is_playing() or vc.is_paused()):
            if queue:
                queue.add(player)
            embed = discord.Embed(
                title="📝 Added to Queue", 
                description=f"🎵 **{player.title}**\n🎤 Uploader: {player.uploader}", 
                color=discord.Color.green()
            )
            if player.duration and player.duration > 0:
                embed.add_field(name="⏱️ Duration", value=player.format_duration(), inline=True)
            embed.add_field(name="📍 Position in Queue", value=str(len(queue.queue) if queue else 0), inline=True)
            if player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)
            embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed)
        else:
            if vc and isinstance(vc, discord.VoiceClient) and player:
                vc.play(player, after=lambda e: self.play_next_song(guild))
            if queue:
                queue.current = player
            embed = discord.Embed(
                title="🎵 Now Playing", 
                description=f"**{player.title}**\n🎤 Uploader: {player.uploader}", 
                color=discord.Color.blurple()
            )
            if player.duration and player.duration > 0:
                embed.add_field(name="⏱️ Duration", value=player.format_duration(), inline=True)
            next_song = queue.queue[0].title if queue and len(queue.queue) > 0 else "Nothing in queue"
            embed.add_field(name="📅 Next Up", value=next_song, inline=True)
            if player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)
            embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=MusicControls(self, guild.id if guild else 0))

    @app_commands.command(name="skip", description="⏭️ Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient):
            return await interaction.response.send_message(embed=self._make_embed("❗ Not connected to a voice channel.", discord.Color.red()))
        if not vc.is_playing():
            return await interaction.response.send_message(embed=self._make_embed("❗ No music is currently playing.", discord.Color.red()))
        vc.stop()
        await interaction.response.send_message(embed=self._make_embed("⏭️ Skipped the current song!", discord.Color.orange()))

    @app_commands.command(name="stop", description="⏹️ Stop music and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient):
            return await interaction.response.send_message(embed=self._make_embed("❗ Not connected to a voice channel.", discord.Color.red()))
        vc.stop()
        queue = self.get_queue(guild.id) if guild else None
        if queue:
            queue.clear()
        await interaction.response.send_message(embed=self._make_embed("⏹️ Stopped music and cleared the queue!", discord.Color.red()))

    @app_commands.command(name="queue", description="📜 Show the current queue")
    async def show_queue(self, interaction: discord.Interaction):
        guild = interaction.guild
        queue = self.get_queue(guild.id) if guild else None
        if not queue or (not queue and not queue.current):
            return await interaction.response.send_message(embed=self._make_embed("📭 The queue is empty and nothing is playing.", discord.Color.light_grey()))
        embed = discord.Embed(title="📜 Music Queue", color=discord.Color.green())
        if queue.current:
            embed.add_field(
                name="🎵 Now Playing", 
                value=f"**{queue.current.title}**\n🎤 {queue.current.uploader}\n⏱️ {queue.current.format_duration()}", 
                inline=False
            )
        if queue:
            queue_list = []
            for i, song in enumerate(queue.queue[:10]):
                duration = song.format_duration()
                queue_list.append(f"{i+1}. **{song.title}** - {duration}")
            if len(queue.queue) > 10:
                queue_list.append(f"... and {len(queue.queue) - 10} more songs")
            embed.add_field(name="📅 Up Next", value="\n".join(queue_list), inline=False)
        else:
            embed.add_field(name="📅 Up Next", value="Nothing in queue", inline=False)
        embed.set_footer(text=f"Total songs in queue: {len(queue.queue) if queue else 0}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pause", description="⏸️ Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient) or not vc.is_playing():
            return await interaction.response.send_message(embed=self._make_embed("❗ No music is currently playing.", discord.Color.red()))
        vc.pause()
        await interaction.response.send_message(embed=self._make_embed("⏸️ Music paused!", discord.Color.orange()))

    @app_commands.command(name="resume", description="▶️ Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient) or not vc.is_paused():
            return await interaction.response.send_message(embed=self._make_embed("❗ Music is not paused.", discord.Color.red()))
        vc.resume()
        await interaction.response.send_message(embed=self._make_embed("▶️ Music resumed!", discord.Color.green()))

    @app_commands.command(name="leave", description="👋 Disconnect from voice channel")
    async def leave(self, interaction: discord.Interaction):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient):
            return await interaction.response.send_message(embed=self._make_embed("❗ Not connected to a voice channel.", discord.Color.red()))
        await vc.disconnect(force=False)
        queue = self.get_queue(guild.id) if guild else None
        if queue:
            queue.clear()
        await interaction.response.send_message(embed=self._make_embed("👋 Disconnected from voice channel and cleared queue!", discord.Color.orange()))

    @app_commands.command(name="remove", description="🗑️ Remove a song from queue")
    async def remove(self, interaction: discord.Interaction, position: int):
        guild = interaction.guild
        queue = self.get_queue(guild.id) if guild else None
        if not queue:
            return await interaction.response.send_message(embed=self._make_embed("❗ No queue found.", discord.Color.red()))
        if position < 1 or position > len(queue.queue):
            return await interaction.response.send_message(embed=self._make_embed("❗ Invalid position in queue.", discord.Color.red()))
        removed_song = queue.remove(position - 1)
        if removed_song:
            await interaction.response.send_message(embed=self._make_embed(f"🗑️ Removed **{removed_song.title}** from queue!", discord.Color.green()))
        else:
            await interaction.response.send_message(embed=self._make_embed("❗ Failed to remove song from queue.", discord.Color.red()))

    @app_commands.command(name="loop", description="🔁 Toggle loop mode")
    async def loop(self, interaction: discord.Interaction):
        guild = interaction.guild
        queue = self.get_queue(guild.id) if guild else None
        if not queue:
            return await interaction.response.send_message(embed=self._make_embed("❗ No queue found.", discord.Color.red()))
        queue.loop = not queue.loop
        status = "enabled" if queue.loop else "disabled"
        await interaction.response.send_message(embed=self._make_embed(f"🔁 Loop mode {status}!", discord.Color.green()))

    @app_commands.command(name="help", description="ℹ️ Show help information")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Music Bot Commands", color=discord.Color.teal())
        embed.add_field(name="/play [url/search]", value="Play a song from YouTube or search", inline=False)
        embed.add_field(name="/skip", value="Skip the current song", inline=False)
        embed.add_field(name="/stop", value="Stop music and clear queue", inline=False)
        embed.add_field(name="/pause", value="Pause the current song", inline=False)
        embed.add_field(name="/resume", value="Resume paused music", inline=False)
        embed.add_field(name="/queue", value="View the current queue", inline=False)
        embed.add_field(name="/remove [position]", value="Remove a song from queue", inline=False)
        embed.add_field(name="/loop", value="Toggle loop mode", inline=False)
        embed.add_field(name="/leave", value="Disconnect from voice channel", inline=False)
        embed.set_footer(text="Music Bot | Use these commands to control music playback")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def play_next_song(self, guild):
        """Play next song in queue"""
        queue = self.get_queue(guild.id) if guild else None
        if queue and queue.loop and queue.current:
            queue.add(queue.current)
        if queue and len(queue.queue) > 0:
            next_song = queue.get_next()
            vc = guild.voice_client if guild else None
            if vc and isinstance(vc, discord.VoiceClient) and next_song:
                vc.play(next_song, after=lambda e: self.play_next_song(guild))
                queue.current = next_song
        else:
            if queue:
                queue.current = None

    @tasks.loop(minutes=2.0)
    async def leave_check(self):
        """Check and leave voice channel if no one is listening"""
        for vc in list(self.bot.voice_clients):
            channel = getattr(vc, "channel", None)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                continue
            if not vc.is_playing() and not vc.is_paused():
                members = [member for member in channel.members if not member.bot]
                if len(members) == 0:
                    await vc.disconnect(force=False)
                    queue = self.get_queue(vc.guild.id) if hasattr(vc, "guild") and vc.guild else None
                    if queue:
                        queue.clear()

    @leave_check.before_loop
    async def before_leave_check(self):
        await self.bot.wait_until_ready()

    def _make_embed(self, text, color):
        return discord.Embed(description=text, color=color)

class MusicControls(discord.ui.View):
    def __init__(self, music: Music, guild_id: int):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.music = music
        self.guild_id = guild_id
        self.message = None

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient) or not vc.is_playing():
            return await interaction.response.send_message("❗ No music is currently playing.", ephemeral=True)
        
        vc.pause()
        await interaction.response.send_message("⏸️ Music paused!", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient) or not vc.is_paused():
            return await interaction.response.send_message("❗ Music is not paused.", ephemeral=True)
        
        vc.resume()
        await interaction.response.send_message("▶️ Music resumed!", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient) or not vc.is_playing():
            return await interaction.response.send_message("❗ No music is currently playing.", ephemeral=True)
        
        vc.stop()
        await interaction.response.send_message("⏭️ Skipped the current song!", ephemeral=True)

    @discord.ui.button(label="👋 Leave", style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not isinstance(vc, discord.VoiceClient):
            return await interaction.response.send_message("❗ Not connected to a voice channel.", ephemeral=True)
        
        await vc.disconnect(force=False)
        queue = self.music.get_queue(self.guild_id) if self.guild_id else None
        if queue:
            queue.clear()
        await interaction.response.send_message("👋 Disconnected and cleared queue!", ephemeral=True)

    async def on_timeout(self):
        # Disable buttons when timeout
        for item in self.children:
            if hasattr(item, 'disabled'):
                try:
                    item.disabled = True
                except Exception:
                    pass
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        if bot.user:
            print(f"✅ Logged in as {bot.user.name}")
            print(f"🆔 Bot ID: {bot.user.id}")
            logger.info(f"Bot started successfully: {bot.user.name}")
        print(f"✅ Synced {len(synced)} command(s)")
        print(f"📊 Connected to {len(bot.guilds)} guild(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        logger.error(f"Failed to sync commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates"""
    if member.bot:
        return
    
    # If bot is in voice channel and no other members
    for vc in bot.voice_clients:
        channel = getattr(vc, "channel", None)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            continue
        if len([m for m in channel.members if not m.bot]) == 0:
            # Wait 30 seconds then disconnect if still no one
            await asyncio.sleep(30)
            if len([m for m in channel.members if not m.bot]) == 0:
                await vc.disconnect(force=False)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    logger.error(f"Command error: {error}")
    await ctx.send(f"❌ An error occurred: {str(error)}")

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        if TOKEN and isinstance(TOKEN, str):
            await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        print("🚀 Starting Discord Music Bot...")
        print(f"📝 Token loaded: {'Yes' if TOKEN else 'No'}")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        logger.error(f"Bot crashed: {e}")