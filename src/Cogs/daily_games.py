import discord
from discord.ext import commands
import discord.utils
from ..modules import daily_games
import io
import asyncio
from ..modules import response_utils
from discord.ext import pages
from ..modules.daily_games.help import get_help_paginator

import sqlalchemy.exc

class GameStatistics(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dailies_command_group = discord.SlashCommandGroup(
        "dailies", "Statistics from daily games"
    )


    setup_perms = discord.Permissions()
    setup_perms.manage_channels = True
    dailies_setup_command_group = discord.SlashCommandGroup(
        "dailies-debug", "Setup for the daily games module", default_member_permissions = setup_perms
    )



    @dailies_command_group.command(description="Information about using the dailies commands")
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def help(self, ctx: discord.ApplicationContext, ephemeral=True):
        paginator: pages.Paginator = get_help_paginator()
        await paginator.respond(ctx.interaction, ephemeral=ephemeral)


    @dailies_command_group.command(
        description="Post a graph with game scores. Make sure you ingested them first, see /dailies help."
    )
    @discord.option(
        "game",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
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
        
        if not game in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return

        try:
            file = await daily_games.generate_multiuser_graph(
                game, player_1, player_2, player_3, player_4, dates_instead_of_numbers, scatter_instead_of_line
            )
            await ctx.response.send_message(file=file)
        except ValueError as e: 
            await response_utils.send_error_response(ctx, "No scores found for selected users. They most likely weren't ingested.")



    @dailies_command_group.command(
        description="Post a jointgraph with game scores."
    )
    @discord.option(
        "game_x",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
        description="What game on x axis",
    )    
    @discord.option(
        "game_y",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
        description="What game on y axis",
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
        "graph_type",
        type=str,
        choices=daily_games.joint_graph_types.keys(),
        default="Kernel Density Estimate",
        description="What graph to draw",
    )
    async def joint_graph(
        self,
        ctx: discord.ApplicationContext,
        game_x,
        game_y,
        player_1,
        player_2,
        player_3,
        player_4,
        graph_type
    ):
        
        if not game_x in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return        
        if not game_y in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return

        try:
            file = await daily_games.generate_multiuser_jointgraph(
                game_x, game_y, player_1, player_2, player_3, player_4, graph_type
            )
            await ctx.response.send_message(file=file)
        except ValueError as e: 
            await response_utils.send_error_response(ctx, f"No scores found for selected users. {e.args}.")



    @dailies_command_group.command(
        description="Post a users graph with game scores. Make sure you ingested them first, see /dailies help."
    )
    @discord.option(
        "game",
        type=str,required=True,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
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
        if not game in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return
        try:
            file = await daily_games.generate_user_graph(
                game, user, graph_type, dates_instead_of_numbers
            )
            await ctx.response.send_message(file=file)
        except ValueError as e: 
            
            await response_utils.send_error_response(ctx, "No scores found for selected user. They most likely weren't ingested.")


    @dailies_command_group.command(description="Returns users scores in a game.")
    @discord.option(
        "game",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
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
        if not game in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return
        if user is None:
            user = ctx.user

        scores = await daily_games.raw_game_user_data(game, user.id)

        if len(scores) == 0:
            await response_utils.send_error_response(ctx, f"User {user.name} has no saved scores for {game}")
            return
        
        output = io.StringIO()
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



    @dailies_command_group.command(description="Shows which recently played games you forgot about today.")
    @discord.option(
        "user",
        type=discord.SlashCommandOptionType.user,
        description="User, defauls to you.",
        required=False
    )  
    @discord.option("verbose", type=bool, default=False, description="More details")
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def most_recent_games(self, ctx: discord.ApplicationContext, user, verbose, ephemeral):

        if user is None:
            user = ctx.user

        lookback = 21 if verbose else 3

        scores = await daily_games.get_recently_played_games_for_user(user, lookback)

        if len(scores) == 0:
            await response_utils.send_error_response(ctx, f"User {user.name} has no recently saved scores.")
            return
        
        embed = response_utils.latest_games_into_a_table(input_list=scores, username=user.name, verbose=verbose)

        await ctx.response.send_message(
            content=None, ephemeral=ephemeral, embed=embed
        )



    @dailies_command_group.command(description="Get information about a game.")
    @discord.option(
        "game",
        type=str,
        autocomplete=discord.utils.basic_autocomplete(daily_games.available_games),
        description="What game",
    )
    @discord.option("ephemeral", type=bool, default=True, description="Should the output be hidden from others")
    async def game_info(self, ctx: discord.ApplicationContext, game, ephemeral):
        if not game in [x.name for x in daily_games.available_games]:
            await response_utils.send_error_response(ctx, "Unknown game")
            return
        info = daily_games.get_game_info(game)
        embed = response_utils.format_game_info_into_embed(info)
        await ctx.respond( embed=embed, ephemeral=ephemeral)


    @dailies_setup_command_group.command(
        description="Ingest or forget scores in channels. "
    )
    @discord.option(
        "options",
        type=str,
        choices=["Ingest", "Reingest", "Forget"],
        description="What operation to do",
    )
    async def channel_ingestion(self, ctx: discord.ApplicationContext, options):
        match options:
            case "Ingest": 
                await self.ingest_channel_history(ctx)
            case "Reingest":
                await self.reingest_channel_history(ctx)
            case "Forget":
                await self.forget_channel_history(ctx)
            case _ :
                await response_utils.send_error_response(ctx, "Unknown options argument")

    async def ingest_channel_history(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await daily_games.ingest_games_in_channel_from_context(ctx)
        await response_utils.send_success_webhook(ctx.followup, "Ingested this channel.")


    async def reingest_channel_history(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await daily_games.reingest_games_in_channel(ctx)
        await response_utils.send_success_webhook(ctx.followup, "Reingested this channel.")


    async def forget_channel_history(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        await daily_games.release_games_in_channel(ctx)
        await response_utils.send_success_webhook(ctx.followup, "Forgotten scores in this channel.")



    @dailies_setup_command_group.command(
        description="Register and unregister channels."
    )
    @discord.option(
        "options",
        type=str,
        choices=["Register channel", "Unregister channel", "Print registered channels"],
        description="What operation to do in the current channel",
    )
    async def channel_registration(self, ctx: discord.ApplicationContext, options):
        match options:
            case "Register channel":
                await self.register_channel(ctx)
            case "Unregister channel":
                await self.unregister_channel(ctx)
            case "Print registered channels":
                await self.print_registered_channels(ctx)
            case _ :
                await response_utils.send_error_response(ctx, "Unknown options argument")

    async def register_channel(self, ctx: discord.ApplicationContext):       
        try:
            await daily_games.register_channel(ctx)
            await response_utils.send_success_response(ctx, "Succesfully registered")

        except sqlalchemy.exc.IntegrityError as e:
            await response_utils.send_error_response(ctx, "Failed to register. Channel already in database.", "Registration Error")

    async def unregister_channel(self, ctx: discord.ApplicationContext):
        try:
            await daily_games.unregister_channel(ctx)
            await response_utils.send_success_response(ctx, "Succesfully unregistered")
        except sqlalchemy.exc.IntegrityError as e:
            await response_utils.send_error_response(ctx, "Failed to unregister. Channel is not registered.", "Registration Error")
    
    async def print_registered_channels(self, ctx: discord.ApplicationContext):
        ids = await daily_games.get_registered_channel_ids_in_guild(ctx)
        result = ""

        if ctx.guild is None:
            await response_utils.send_error_response(ctx, "Not in a guild.")

        for id in ids:
            guild: discord.Guild = ctx.guild
            channel = guild.get_channel_or_thread(id)

            if channel is None:
                continue

            result += f" {channel.name} \n"

        await response_utils.send_success_response(ctx, result, "Following channels/threads are registered.")


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        if not await daily_games.in_registered_channel(message):
            return

        await daily_games.ingest_message(message)

        await asyncio.sleep(200)
        fixed_link = await daily_games.get_a_fixed_link(message)
        if fixed_link is not None:
            await message.channel.send(f"<{fixed_link}>")

    @commands.Cog.listener()
    async def on_ready(self):
        result = await daily_games.get_all_registered_channel_ids()

        for channel_id in result:
            channel = self.bot.get_channel(channel_id)
            await daily_games.ingest_games_in_channel(channel=channel, limit=80)


    @commands.Cog.listener()
    async def on_message_edit(self, message_before: discord.Message, message_after: discord.Message):

            if message_after.author == self.bot.user:
                return

            if not await daily_games.in_registered_channel(message_after):
                return
            
            await daily_games.on_message_edit(message_after)

            
            