import discord
import datetime
import re
from typing import Callable
import discord
import datetime
import logging


from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy

from .. import database
import discord

import re

from .models import RegisteredChannels, Scores
from . import utils


logger = logging.getLogger()


registered_parsers: dict[re.Pattern, tuple[Callable, str]] = {}
available_games = []


def register_parser(game_name: str, pattern: str):
    def decorator(func: Callable):
        registered_parsers[re.compile(pattern)] = (func, game_name)
        logger.info(f"Registered parser for the game {game_name} with {func.__name__}")
        return func

    if all([game.name != game_name for game in available_games]):
        available_games.append(discord.OptionChoice(game_name))
    return decorator


async def ingest_message(message: discord.Message):
    contents = message.content

    functions_to_use = []
    games_to_use = []

    for pattern, (func, game) in registered_parsers.items():
        pattern: re.Pattern = pattern
        if pattern.search(contents) is not None:
            functions_to_use.append(func)
            games_to_use.append(game)

    for function, game_name in zip(functions_to_use, games_to_use):
        parsed: tuple[int, datetime.date, int] | None = function(message)

        if (
            parsed is None
        ):  # Happens when the parser cant parse the message, most likely cause the preliminary check isnt robust enough, its okay
            continue

        gamescore, gamedate, gamenumber = parsed
        await send_score_to_database(
            message=message,
            game_name=game_name,
            gamescore=gamescore,
            gamedate=gamedate,
            gamenumber=gamenumber,
        )


async def ingest_games_in_channel(ctx: discord.ApplicationContext, limit=None):
    channel: discord.interactions.InteractionChannel = ctx.channel
    async for msg in channel.history(limit=limit):
        if msg.author.bot == True:
            continue
        await ingest_message(msg)


async def release_games_in_channel(ctx: discord.ApplicationContext):
    async with database.AsyncSessionLocal.begin() as session:
        channel: discord.interactions.InteractionChannel = ctx.channel
        await session.execute(
            sqlalchemy.delete(Scores).where(Scores.channel_id == channel.id)
        )


async def reingest_games_in_channel(ctx: discord.ApplicationContext):
    await release_games_in_channel(ctx)
    await ingest_games_in_channel(ctx)


game_info: dict[str, utils.GameInfo] = {}


def add_game_info(game_name: str, info: utils.GameInfo):
    game_info[game_name] = info


def get_game_info(game_name: str):
    return game_info[game_name]

async def register_channel(ctx: discord.ApplicationContext):
    # sqlalchemy.exc.IntegrityError
    async with database.AsyncSessionLocal.begin() as session:
        channel = RegisteredChannels()
        channel.channel_id = ctx.channel_id
        channel.timestamp_of_registration = discord.utils.utcnow()
        channel.who_registered_user_id = ctx.author.id

        session.add(channel)
    return


async def unregister_channel(ctx: discord.ApplicationContext):
    # sqlalchemy.exc.NoResultFound
    async with database.AsyncSessionLocal.begin() as session:
        channel = await session.get_one(RegisteredChannels, ctx.channel.id)
        await session.delete(channel)


async def in_registered_channel(message: discord.Message):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession
        result = await session.get(RegisteredChannels, message.channel.id)
        return result is not None


async def send_score_to_database(
    message: discord.Message,
    game_name: str,
    gamescore: int,
    gamedate: datetime.date,
    gamenumber: int,
):
    async with database.AsyncSessionLocal.begin() as session:
        score = Scores(
            channel_id=message.channel.id,
            game=game_name,
            message_id=message.id,
            user_id=message.author.id,
            timestamp=message.created_at,
            score=gamescore,
            date_of_game=gamedate,
            game_number=gamenumber,
        )
        session.add(score)


link_association = [
    ("Betweenle", ("https://betweenle.com/", "https://www.betweenle.com/")),
    (
        "REVEALED",
        (
            "https://www.britannica.com/games/revealed",
            "https://britannica.com/games/revealed",
        ),
    ),
    ("VideoPuzzle.org", ("https://videopuzzle.org/", "https://www.videopuzzle.org/")),
    ("catfishing.net", ("https://catfishing.net/", "https://www.catfishing.net/")),
    (
        "syllacrostic.com",
        ("https://syllacrostic.com/", "https://www.syllacrostic.com/"),
    ),
]


async def get_a_fixed_link(message: discord.Message) -> str | None:
    for broken, fixed_messages in link_association:
        if broken in message.content:
            async for msg in message.channel.history(limit=25):
                for fixed in fixed_messages:
                    if fixed in msg.content:
                        return
            return fixed_messages[0]
