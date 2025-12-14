import lyricsgenius
import dotenv

import asyncio
import requests
import discord

dotenv_path :str = "config_files/.env"


config = dotenv.dotenv_values(dotenv_path)


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
genius = lyricsgenius.Genius(access_token=config["GENIUS_TOKEN"], verbose=False, sleep_time=0.01, user_agent=user_agent)




async def song_lyrics(song_name: str, artist_name: str):
    try:
        song = await asyncio.to_thread(genius.search_song, title=song_name, artist=artist_name)
    except requests.exceptions.Timeout:
        song = await asyncio.to_thread(genius.search_song, title=song_name, artist=artist_name)
    return song


async def song_title_from_activities(activities): 
    for x in activities:
        if isinstance(x, discord.activity.Spotify):
            return x.title
        
async def song_main_artist_from_activities(activities): 
    for x in activities:
        if isinstance(x, discord.activity.Spotify):
            return x.artists[0]
    return ""
        
