import discord
from discord.ext import commands
import logging
import io

from ..modules import songs
from ..modules import response_utils

console_logger = logging.getLogger("console")

song_logger = logging.getLogger("songs")


class Songs(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dailies_command_group = discord.SlashCommandGroup(
        "songs", "Commands for working with songs"
    )

    @commands.Cog.listener()
    async def on_ready(self):
        pass 

    @dailies_command_group.command(description="Responds with song lyrics.")
    @discord.option("song_name", type=str, default=None, description="Name of the song, if empty it gets taken from rich presence if possible")
    @discord.option("artist_name", type=str, default="", description="Artist name")
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def lyrics(self, ctx: discord.ApplicationContext, song_name, artist_name="",  ephemeral=True):
        author = ctx.author
        if song_name is None: 

            if isinstance(author, discord.User) and len(author.mutual_guilds)>0:
                author = author.mutual_guilds[0].get_member(author.id)
            
            assert isinstance(author, discord.Member)
            if author is not None:
                song_name = await songs.song_title_from_activities(author.activities)
                artist_name = await songs.song_main_artist_from_activities(author.activities)

        if song_name is None:
            await response_utils.send_error_response(ctx, f"No song specified and couldn't read user activity. In order to get the song from an activity you need to be in a server with the bot.")
            return           

        response = ctx.interaction.response

        await response.defer(ephemeral=ephemeral)


        song_logger.info(f"Retrieving {song_name} for user {author.name} - user id:{author.id}")
        song = await songs.song_lyrics(song_name=song_name, artist_name=artist_name)

        if song is None:
            await response_utils.send_error_webhook(ctx.followup, f"Could not find song: {song_name}")
            return
        

        embed_title = f"\"{song.title}\" by {song.artist}" 

        lyrics = song.lyrics

        if len(lyrics)> 4000:
            lyrics_encoded = io.BytesIO(lyrics.encode())
            file = discord.File(lyrics_encoded, embed_title + ".txt")
            embed = response_utils.default_text_embed(embed_title)
            await ctx.send_followup(embed=embed, file=file, ephemeral=ephemeral)
        else:
            embed = response_utils.default_text_embed(embed_title, text=lyrics)
            await ctx.send_followup(embed=embed, ephemeral=ephemeral)
