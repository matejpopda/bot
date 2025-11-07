import seaborn as sns
import discord
from .daily_games.utils import GameInfo


def set_default_graph_formatting():
    sns.set_theme(style="darkgrid")


def format_game_info_into_embed(info: GameInfo):
    title = f"\"{info.game_name}\" information"
    description = f"{info.description}"
    embed = discord.Embed(color=discord.Colour.blue(), title=title, description=description)

    embed.add_field(name="Play at", value=info.url)

    return embed

def string_to_pages_embed(text, title=None, footer=None):
    embed = discord.Embed(color=discord.Colour.blue(), title=title, description=text)
    embed.set_footer(text=footer)
    return embed
    
def string_to_error_embed(text, error_title="Error"):
    embed = discord.Embed(color=discord.Colour.red(), title=error_title, description=text)
    return embed

def string_to_success_embed(text, title="Success"):
    embed = discord.Embed(color=discord.Colour.blue(), title=title, description=text)
    return embed

async def send_success_response(ctx: discord.ApplicationContext, text, title="Success", ephemeral=True):
    embed = string_to_success_embed(text, title)
    await ctx.response.send_message(
        embed=embed, ephemeral=ephemeral
    )

async def send_error_response(ctx: discord.ApplicationContext, text, title="Error", ephemeral=True):
    embed = string_to_error_embed(text, title)
    await ctx.response.send_message(
        embed=embed, ephemeral=ephemeral
    )

async def send_success_webhook(webhook: discord.Webhook, text, title="Success", ephemeral=True):
    embed = string_to_success_embed(text, title)
    await webhook.send(
        embed=embed, ephemeral=ephemeral
    )

async def send_error_webhook(webhook: discord.Webhook, text, title="Error", ephemeral=True):
    embed = string_to_error_embed(text, title)
    await webhook.send(
        embed=embed, ephemeral=ephemeral
    )