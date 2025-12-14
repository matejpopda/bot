import seaborn as sns
import discord
from .daily_games.utils import GameInfo
from .daily_games.models import Scores
import datetime
import prettytable


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
    

def default_text_embed(title, text=None, footer=None, image=None):
    embed = discord.Embed(color=discord.Colour.blue(), title=title, description=text, image=image)
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
        embed=embed, ephemeral=ephemeral, delete_after=20
    )

def latest_games_into_a_table(input_list: list[Scores], username, verbose):
    todays_date =  datetime.datetime.now(datetime.timezone.utc).date()

    table = prettytable.PrettyTable()
    table.field_names = [ "Game", "🕹️", "Score","Played on"]


    for score in input_list:
        if (score.date_of_game == todays_date):
            played_today = "✅"
        elif verbose and (score.date_of_game == todays_date - datetime.timedelta(days=2) or score.date_of_game == todays_date - datetime.timedelta(days=1)):
            played_today = "⚠️"
        else: 
            played_today = "⛔"

        table.add_row([score.game, played_today, score.score, score.date_of_game])


    table.set_style(prettytable.TableStyle.SINGLE_BORDER)
    table.padding_width = 0
    table.max_width = 18
    if verbose:
        description = table.get_string()
    else: 
        description = table.get_string(fields=["🕹️", "Game"])


    title = f"Most recent saved games  by {username}"
    embed = discord.Embed(color=discord.Colour.blue(), title=title, description=f"```{description}```")


    return embed





