
import discord
import datetime
import logging
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from ..modules import database
from collections.abc import Callable

import re

class RegisteredChannels(database.Base):
    __tablename__ = "registered_channels"
    channel_id: Mapped[int] = mapped_column(primary_key=True)
    who_registered_user_id: Mapped[int] 
    timestamp_of_registration: Mapped[datetime.datetime]




class Scores(database.Base):
    __tablename__ = "scores"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[float]
    user_id: Mapped[int] 
    channel_id: Mapped[int]
    game: Mapped[str] 
    date_of_game: Mapped[datetime.date]
    # game_number: Mapped[int]
    timestamp: Mapped[datetime.datetime]









async def ingest_games_in_channel(ctx:discord.ApplicationContext):
    channel:discord.interactions.InteractionChannel = ctx.channel
    async for msg in channel.history():
        if msg.author.bot == True:
            continue
        await ingest_message(msg)


async def register_channel(ctx:discord.ApplicationContext):
    #sqlalchemy.exc.IntegrityError    
    async with database.AsyncSessionLocal.begin() as session:
        channel = RegisteredChannels()
        channel.channel_id = ctx.channel_id
        channel.timestamp_of_registration = discord.utils.utcnow()
        channel.who_registered_user_id = ctx.author.id

        session.add(channel)
    return

async def unregister_channel(ctx:discord.ApplicationContext):
    #sqlalchemy.exc.NoResultFound    
    async with database.AsyncSessionLocal.begin() as session:
        channel = await session.get_one(RegisteredChannels, ctx.channel_id)
        await session.delete(channel)


async def in_registered_channel(message: discord.Message):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession
        result = await session.get(RegisteredChannels, message.channel_id)
        return result is not None
    

async def raw_game_data(game:str, user_id):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession

        result = []

        query = await session.execute(sqlalchemy.select(Scores).where(Scores.user_id == user_id).where(Scores.game == game))
        for score in query.scalars():
            result.append({"score":score.score, 
                           "game":score.game, 
                           "date": score.date_of_game})

        return result


registered_parsers: dict[re.Pattern, tuple[Callable, str]] = {}
available_games = []


def register_parser(game_name: str, pattern:str):
    def decorator(func):
        registered_parsers[re.compile(pattern)] = (func, game_name)
        return func
    
    if all([game.name != game_name for game in available_games]):
        available_games.append(discord.OptionChoice(game_name))
    return decorator


async def ingest_message(message: discord.Message):
    contents = message.content

    function_to_use = None
    game_to_use = None
    
    for pattern, (func, game) in registered_parsers.items():
        pattern: re.Pattern = pattern
        # print(message)
        if pattern.match(contents):
            # print(message)
            # print(func, game, "here")
            if function_to_use is not None:
                logging.warning("While ingesting a message in gamestatistics.py, there were multiple available parsers")
                logging.warning("Message was: " + contents)
                logging.warning(f"Game 1 was {game} and game 2 was {game_to_use}")
            function_to_use = func
            game_to_use = game

    # print(game_to_use)
    if function_to_use is None:
        return
    
    gamescore, gamedate = function_to_use(contents)

    async with database.AsyncSessionLocal.begin() as session:
        score = Scores(channel_id = message.channel.id,
                       game = game_to_use,
                       message_id = message.id,
                       user_id = message.author.id,
                       timestamp = message.created_at,
                       score = gamescore,
                       date_of_game = gamedate)
        session.add(score)
        print(score)




@register_parser("Coindle", r"Coindle")
def coindle_date_and_score(text: str) -> tuple[int, datetime.date] | None:
    date_match = re.search(r"Coindle (\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
    streak_match = re.search(r"Streak:\s*(\d+)", text)
    
    if date_match and streak_match:
        date_str = date_match.group(1)
        streak = int(streak_match.group(1))
        date_obj = datetime.date.fromisoformat(date_str)
        return streak, date_obj






type User = discord.SlashCommandOptionType.user
async def generate_graph(game: discord.OptionChoice, player_1: User, player_2: User|None, player_3: User|None, player_4: User|None):
    return
