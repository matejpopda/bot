import discord
from discord.ext import commands
from ..modules import daily_games
import io
import asyncio
from ..modules import formatting

import sqlalchemy.exc

class GameStatistics(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    command_group = discord.SlashCommandGroup(
        "dailies", "Statistics from daily games"
    )

    @command_group.command(description="Information about using the gamestats commands")
    async def help(self, ctx: discord.ApplicationContext):

        await ctx.respond()

    @command_group.command(
        description="Post a graph with game scores. Make sure you ingested them first, see /gamestats help."
    )
    @discord.option(
        "game",
        type=str,
        choices=daily_games.available_games,
        description="What game",
    )
    @discord.option(
        "player_1",
        type=discord.SlashCommandOptionType.user,
        required=True,
        description="Player 1",
    )
    @discord.option(
        "player_2",
        type=discord.SlashCommandOptionType.user,
        required=False,
        description="Player 2",
    )
    @discord.option(
        "player_3",
        type=discord.SlashCommandOptionType.user,
        required=False,
        description="Player 3",
    )
    @discord.option(
        "player_4",
        type=discord.SlashCommandOptionType.user,
        required=False,
        description="Player 4",
    )
    @discord.option(
        "dates_instead_of_numbers",
        type=bool,
        default=False,
        description="Plot against dates instead of game numbers.",
    )
    @discord.option(
        "scatter_instead_of_line",
        type=bool,
        default=False,
        description="Make a scatter plot instead of a line plot.",
    )
    async def multi_graph(
        self,
        ctx: discord.ApplicationContext,
        game,
        player_1,
        player_2,
        player_3,
        player_4,
        dates_instead_of_numbers,scatter_instead_of_line,
    ):

        try:
            file = await daily_games.generate_multiuser_graph(
                game, player_1, player_2, player_3, player_4, dates_instead_of_numbers, scatter_instead_of_line
            )
            await ctx.response.send_message(file=file)
        except ValueError as e: 
            await ctx.response.send_message("No scores found for selected users. They most likely weren't ingested.", ephemeral=True)



    @command_group.command(
        description="Post a users graph with game scores. Make sure you ingested them first, see /gamestats help."
    )
    @discord.option(
        "game",
        type=str,required=True,
        choices=daily_games.available_games,
        description="What game",
    )

    @discord.option(
        "user",
        type=discord.SlashCommandOptionType.user,
        required=True,
        description="User",
    )
    @discord.option(
        "graph_type",
        type=str,
        choices=daily_games.user_graph_types,
        description="What graph to draw",
    )
    @discord.option(
        "dates_instead_of_numbers",
        type=bool,
        default=False,
        description="Plot against dates instead of game numbers.",
    )
    async def user_graph(
        self,
        ctx: discord.ApplicationContext,
        game,
        user,
        graph_type,
        dates_instead_of_numbers,
    ):

        try:
            file = await daily_games.generate_user_graph(
                game, user, graph_type, dates_instead_of_numbers
            )
            await ctx.response.send_message(file=file)
        except ValueError as e: 
            await ctx.response.send_message("No scores found for selected users. They most likely weren't ingested.", ephemeral=True)


    @command_group.command(description="Returns users scores in a game.")
    @discord.option(
        "game",
        type=str,
        choices=daily_games.available_games,
        description="What game",
    )
    @discord.option(
        "user",
        type=discord.SlashCommandOptionType.user,
        description="User, defauls to you.",
        required=False
    )
    @discord.option("format", type=str, choices=["human-readable", "csv"], default="human-readable", description="Output format")
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def user_stats(self, ctx: discord.ApplicationContext, game, user, format, ephemeral):
        output = io.StringIO()

        if user is None:
            user = ctx.user

        scores = await daily_games.raw_game_user_data(game, user.id)

        if format == "csv":
            output.write("date, game_number, score\n")
        for score in scores:
            match format:
                case "human-readable":
                    line = f"{score["date"].isoformat()} - Game {score["gamenumber"]} - Score {score["score"]}\n"
                case "csv":
                    line = f"{score["date"].isoformat()}, {score["gamenumber"]}, {score["score"]}\n"

            output.write(
                line
            )

        output.seek(0)
        file = discord.File(fp=output, filename=f"{game}-scores-for-{user.name}.txt")

        await ctx.response.send_message(
            content=f"Here are {user.display_name} scores for {game}", ephemeral=ephemeral, file=file
        )






    @command_group.command(description="Get information about a game.")
    @discord.option(
        "game",
        type=str,
        choices=daily_games.available_games,
        description="What game",
    )
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def game_info(self, ctx: discord.ApplicationContext, game, ephemeral):

        info = daily_games.get_game_info(game)
        embed = formatting.print_game_info(info)
        await ctx.respond( embed=embed, ephemeral=ephemeral)




    @command_group.command(
        description="Goes through all the messages in the channel and saves them"
    )
    async def ingest_channel_history(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await daily_games.ingest_games_in_channel(ctx)
        await ctx.followup.send(content="Ingested", ephemeral=True)

    @command_group.command(
        description="Deletes all data from a channel and then ingests them again."
    )
    async def reingest_channel_history(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await daily_games.reingest_games_in_channel(ctx)
        await ctx.followup.send(content="Ingested", ephemeral=True)


    @command_group.command(
        description="Registers channel, so it automatically saves the scores."
    )
    async def register_channel(self, ctx: discord.ApplicationContext):
            
        try:
            await daily_games.register_channel(ctx)
            await ctx.response.send_message(
                content="Succesfully registered", ephemeral=True
            )

        except sqlalchemy.exc.IntegrityError as e:
            await ctx.response.send_message(
                content="Failed to register. Channel already in database.", ephemeral=True
            )


    @command_group.command(
        description="Unregisters channel, so it no longer automatically saves the scores"
    )
    async def unregister_channel(self, ctx: discord.ApplicationContext):

        try:
            await daily_games.unregister_channel(ctx)

            await ctx.response.send_message(
                content="Succesfully unregistered", ephemeral=True
            )
        except sqlalchemy.exc.NoResultFound as e:
            await ctx.response.send_message(
                content="Failed to unregister. Channel was not registered.", ephemeral=True
            )


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        if not await daily_games.in_registered_channel(message):
            return

        await daily_games.ingest_message(message)

        fixed_link = await daily_games.get_a_fixed_link(message)
        if fixed_link is not None:
            await message.channel.send(f"<{fixed_link}>")

