import discord
from discord.ext import commands
from ..modules import gamestatistics
import io 
import asyncio

class GameStatistics(commands.Cog):
    
    def __init__(self, bot: commands.Bot): 
        self.bot = bot


    command_group = discord.SlashCommandGroup("gamestats", "Statistics from daily games")

    @command_group.command(description="Information about using the gamestats commands") 
    async def help(self, ctx:discord.ApplicationContext):

        await ctx.respond() 

    @command_group.command(description="Post a graph with game scores. Make sure you ingested them first, see /gamestats help.") 
    @discord.option("game", type=str, choices=gamestatistics.available_games, description="What game")
    @discord.option("player_1", type=discord.SlashCommandOptionType.user, required=True, description="Player 1")
    @discord.option("player_2", type=discord.SlashCommandOptionType.user, required=False, description="Player 2")
    @discord.option("player_3", type=discord.SlashCommandOptionType.user, required=False, description="Player 3")
    @discord.option("player_4", type=discord.SlashCommandOptionType.user, required=False, description="Player 4")
    @discord.option("dates_instead_of_numbers", type=bool, default=False, description="Plot against dates instead of game numbers.")
    async def statistics(self, ctx:discord.ApplicationContext, game, player_1, player_2, player_3, player_4, dates_instead_of_numbers):
        
        file = await gamestatistics.generate_graph(game, player_1, player_2, player_3, player_4, dates_instead_of_numbers)
        await ctx.response.send_message(file=file)


    @command_group.command(description="Returns your scores in a game.") 
    @discord.option("game", type=str, choices=gamestatistics.available_games, description="What game")
    async def my_stats(self, ctx:discord.ApplicationContext, game):
        output = io.StringIO()
        scores = await gamestatistics.raw_game_data(game, ctx.user.id)
        for score in scores:
            output.write(f"{score["date"].isoformat()} - Game {score["gamenumber"]} - Score {score["score"]}\n")

        output.seek(0)
        file = discord.File(fp=output, filename="results.txt")
        
        await ctx.response.send_message(content=f"Here are your scores for {game}", ephemeral=True, file=file)


    @command_group.command(description="Returns scores in a game for a user.") 
    @discord.option("game", type=str, choices=gamestatistics.available_games, description="What game")
    @discord.option("user", type=discord.SlashCommandOptionType.user, description="User, defauls to you.")
    async def user_stats(self, ctx:discord.ApplicationContext, game, user):
        output = io.StringIO()

        if user is None:
            user = ctx.user.id

        scores = await gamestatistics.raw_game_data(game, user.id)
        for score in scores:
            output.write(f"{score["date"].isoformat()} - Game {score["gamenumber"]} - Score {score["score"]}\n")

        output.seek(0)
        file = discord.File(fp=output, filename="results.txt")
        
        await ctx.response.send_message(content=f"Here are your scores for {game}", ephemeral=True, file=file)


    @command_group.command(description="Goes through all the messages in the channel and saves them") 
    async def ingest_channel_history(self, ctx:discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await gamestatistics.ingest_games_in_channel(ctx)
        await ctx.followup.send(content="Ingested", ephemeral=True)

    @command_group.command(description="Goes through all the messages in the channel and saves them") 
    async def reingest_channel_history(self, ctx:discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await gamestatistics.reingest_games_in_channel(ctx)
        await ctx.followup.send(content="Ingested", ephemeral=True)


    @command_group.command(description="Registers channel, so it automatically saves the scores") 
    async def register_channel(self, ctx:discord.ApplicationContext):
        await gamestatistics.register_channel(ctx)
        
        await ctx.response.send_message(content="Succesfully registered", ephemeral=True)


    @command_group.command(description="Unregisters channel, so it no longer automatically saves the scores") 
    async def unregister_channel(self, ctx:discord.ApplicationContext):
        await gamestatistics.unregister_channel(ctx)
        
        await ctx.response.send_message(content="Succesfully unregistered", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return
        

        if not  await gamestatistics.in_registered_channel(message):
            return
        

        
        await gamestatistics.ingest_message(message)



