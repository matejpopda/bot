import lyricsgenius
import dotenv

import asyncio

import discord

dotenv_path :str = "config_files/.env"


config = dotenv.dotenv_values(dotenv_path)

genius = lyricsgenius.Genius(access_token=config["GENIUS_TOKEN"], verbose=False, sleep_time=0.01)




async def song_lyrics(song_name: str, artist_name: str):
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
        
