import discord
from discord.ext import commands

from ..modules import ttrpgtools

import logging
import d20


roll_template = """```
Rolled {dice_notation}:
Result = {result}```
Roll breakdown: {dice}  
"""


def parse_ctx_to_get_dice_notation(ctx: discord.ApplicationContext):
    logging.debug(ctx.selected_options)
    assert ctx.selected_options is not None
    return next(
        (
            option["value"]
            for option in ctx.selected_options
            if option.get("name") == "dice_notation"
        ),
        None,
    )


class TttrpgTools(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ttrpg = discord.SlashCommandGroup("ttrpg", "ttrpg tools")
    advanced_ttrpg = ttrpg.create_subgroup(
        "advanced", "Tools for modelling probability outcomes"
    )

    @ttrpg.command(description="Make a roll using dice notation")
    @discord.option("dice_notation", type=str, description="Input dice notation")
    async def roll(self, ctx: discord.ApplicationContext, dice_notation: str):
        roll_result = d20.roll(dice_notation)
        response = roll_template.format(
            dice_notation=dice_notation, result=roll_result.total, dice=str(roll_result)
        )
        await ctx.respond(response)

    @ttrpg.command(description="Prints info about the ttrpg submodule")
    async def info(self, ctx: discord.ApplicationContext):
        response = "`This module uses the following library on its backend:` <https://github.com/avrae/d20>`. Consult the website for more advanced syntax.`"
        await ctx.respond(response, ephemeral=True)

    @ttrpg.command(
        description="Simulate rolling and output a probability distribution function"
    )
    @discord.option("dice_notation", type=str, description="Input dice notation")
    @discord.option(
        "cumulative_plot",
        type=bool,
        default=False,
        description="Return the cumulative distribution function as result",
    )
    async def simulate_roll(
        self,
        ctx: discord.ApplicationContext,
        dice_notation: str,
        cumulative_plot: bool = False,
    ):
        file = ttrpgtools.simulate_roll(dice_notation, cumulative_plot)
        await ctx.respond(
            f"Simulated the following dice roll: `{dice_notation}`", file=file
        )

    async def cog_command_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.ApplicationCommandInvokeError,
    ):
        interaction_response = ctx.response

        if isinstance(error.original, d20.RollSyntaxError):
            dice_notation = parse_ctx_to_get_dice_notation(ctx)
            content = (
                f"""```There is an error with the roll syntax:\n"""
                f"""{dice_notation}\n\n"""
                f"""Expected {error.original.expected} at the column {error.original.col}, but got "{error.original.got}" instead```"""
            )
            await interaction_response.send_message(content=content, ephemeral=True)

        elif isinstance(error.original, d20.RollError):
            dice_notation = parse_ctx_to_get_dice_notation(ctx)
            content = f"Error in the dice notation {dice_notation}. \n {error.original}"
            await interaction_response.send_message(content=content, ephemeral=True)

        else:
            raise error
