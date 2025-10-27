import discord
from discord.ext import commands
import dyce
import d20


roll_template = """```
Rolled {dice_notation}:
Result = {result}```
Roll breakdown: {dice}  
"""



class TttrpgTools(commands.Cog):
    
    def __init__(self, bot: discord.Bot): 
        self.bot = bot
        
    ttrpg = discord.SlashCommandGroup("ttrpg", "ttrpg tools")
    advanced_ttrpg = ttrpg.create_subgroup("advanced", "Tools for modelling probability outcomes")

    @ttrpg.command(description="Make a roll using dice notation") 
    @discord.option("dice_notation", type=str, description="Input dice notation")
    async def roll(self, ctx:discord.ApplicationContext, dice_notation:str):


        try:
            roll_result = d20.roll(dice_notation)
            # print(roll_result)
            response = roll_template.format(dice_notation=dice_notation, result=roll_result.total, dice = str(roll_result))

            await ctx.respond(response)
        
        except d20.RollSyntaxError as e:
            error_response = ctx.response

            content =  (f"""```There is an error with the roll syntax:\n"""
                        f"""{dice_notation}\n\n"""
                        f"""Expected {e.expected} at the column {e.col}, but got "{e.got}" instead```""")

            await error_response.send_message(content=content, ephemeral=True)

        except d20.RollError as e:

            error_response = ctx.response

            content = f"Error in the dice notation {dice_notation}. \n {e}" 

            await error_response.send_message(content=content, ephemeral=True)