import seaborn as sns
import discord
from .daily_games.utils import GameInfo


def set_default_graph_formatting():
    sns.set_theme(style="darkgrid")


def print_game_info(info: GameInfo):
    embed = discord.Embed(color=discord.Colour.blue())
    embed.title = f"\"{info.game_name}\" information"
    embed.description = f"{info.description}"
    
    embed.add_field(name="Play at", value=info.url)

    return embed

    
