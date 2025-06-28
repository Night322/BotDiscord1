from setuptools import setup, find_packages

setup(
    name="discord-music-bot",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "discord.py==2.3.2",
        "python-dotenv==1.0.0",
        "yt-dlp==2023.12.30",
        "PyNaCl==1.5.0",
    ],
    python_requires=">=3.8",
    author="Discord Music Bot",
    description="A Discord music bot with YouTube support",
    keywords="discord bot music youtube",
) 