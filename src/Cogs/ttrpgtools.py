import discord
from discord.ext import commands

import logging

import dyce
import numpy as np
import d20
import seaborn as sns
import matplotlib.pyplot as plt
import io


roll_template = """```
Rolled {dice_notation}:
Result = {result}```
Roll breakdown: {dice}  
"""

def parse_ctx_to_get_dice_notation(ctx: discord.ApplicationContext):
    logging.debug(ctx.selected_options)
    return next((option['value'] for option in ctx.selected_options if option.get('name') == 'dice_notation'), None)


class TttrpgTools(commands.Cog):
    
    def __init__(self, bot: discord.Bot): 
        self.bot = bot
        
    ttrpg = discord.SlashCommandGroup("ttrpg", "ttrpg tools")
    advanced_ttrpg = ttrpg.create_subgroup("advanced", "Tools for modelling probability outcomes")

    @ttrpg.command(description="Make a roll using dice notation") 
    @discord.option("dice_notation", type=str, description="Input dice notation")
    async def roll(self, ctx:discord.ApplicationContext, dice_notation:str):
        roll_result = d20.roll(dice_notation)
        response = roll_template.format(dice_notation=dice_notation, result=roll_result.total, dice = str(roll_result))
        await ctx.respond(response)

    @ttrpg.command(description="Prints info about the ttrpg submodule") 
    async def info(self, ctx:discord.ApplicationContext):
        response = "`This module uses the following library on its backend:` <https://github.com/avrae/d20>`. Consult the website for more advanced syntax.`"
        await ctx.respond(response, ephemeral=True)



    @ttrpg.command(description="Simulate rolling and output a probability distribution function") 
    @discord.option("dice_notation", type=str, description="Input dice notation")
    @discord.option("cumulative_plot", type=bool, default=False, description="Return the cumulative distribution function as result")
    async def simulate_roll(self, ctx:discord.ApplicationContext, dice_notation:str, cumulative_plot:bool=False ):
        rolls = 10000

        results = np.array([d20.roll(dice_notation).total for _ in range(rolls)])


        totals = np.arange(results.min(), results.max() + 1)
        counts = np.array([np.sum(results == t) for t in totals])
        pdf = counts / counts.sum()

        avg = np.mean(results)
        mode = np.median(results)
        variance = np.var(results)

        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(6, 4))

        if cumulative_plot == True:
            cdf = np.cumsum(pdf)
            plt.bar(totals, cdf)
        else: 
            plt.bar(totals, pdf)

        # Use the plt.legend in order to write out avg, mode and mean
        plt.axvline(avg, color=(0,0,0,0), linestyle="--", label=f"Mean = {avg:.2f}")
        plt.axvline(mode, color=(0,0,0,0), linestyle="--", label=f"Mode = {mode:.2f}")
        plt.axvline(variance, color=(0,0,0,0), linestyle="--", label=f"Variance = {variance:.2f}")
        plt.legend(markerfirst=False, markerscale=0, handlelength=0)


        plt.title(f"{dice_notation} — {rolls:,} rolls")
        plt.xlabel("Roll Result")
        plt.ylabel("Probability")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=200)
        buf.seek(0)
        plt.close()

        file = discord.File(buf, filename="histogram.png")
        await ctx.respond(f"Simulated the following dice roll: `{dice_notation}`", file=file)



    async def cog_command_error(self, ctx: discord.ApplicationContext, error: discord.ApplicationCommandInvokeError):
        interaction_response = ctx.response

        if isinstance(error.original, d20.RollSyntaxError):
            dice_notation = parse_ctx_to_get_dice_notation(ctx)
            content =  (f"""```There is an error with the roll syntax:\n"""
                        f"""{dice_notation}\n\n"""
                        f"""Expected {error.original.expected} at the column {error.original.col}, but got "{error.original.got}" instead```""")
            await interaction_response.send_message(content=content, ephemeral=True)

        elif isinstance(error.original, d20.RollError):
            dice_notation = parse_ctx_to_get_dice_notation(ctx)
            content = f"Error in the dice notation {dice_notation}. \n {error.original}" 
            await interaction_response.send_message(content=content, ephemeral=True)

        else:
            raise error  
