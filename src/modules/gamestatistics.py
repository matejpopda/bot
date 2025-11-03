
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


import numpy as np
import d20

import seaborn as sns
import matplotlib.pyplot as plt
import io
import discord

import re



COINDLE_FIRST_GAME_DATE=datetime.date(year=2025, month=10, day=8)
MINIGOLFLE_ORIGIN_DATE = datetime.date(day=29, month=9, year=2025)
SYLLACROSTIC_ORIGIN_DATE = datetime.date(day=28, month=3, year=2023)
CATFISHING_ORIGIN_DATE = datetime.date(day=23, month=6, year=2024)
TIMDLE_ORIGIN_DATE = datetime.date(day=26, month=1, year=2025) # Based on wayback machine its somewhere between december 2024 and this date
REUNION_ORIGIN_DATE = datetime.date(day=8, month=10, year=2025)
AKARI_ORIGIN_DATE = datetime.date(day=5, month=1, year=2025)
WIKI_GAME_DAILY_ORIGIN_DATE = datetime.date(day=17, month=7, year=2024) # Based on wayback machine
REVEALED_ORIGIN_DATE = datetime.date(day=6, month=10, year=2025)
WORDLE_ORIGIN_DATE = datetime.date(day=19, month=6, year=2021)
COSTCODLE_ORIGIN_DATE = datetime.date(day=19, month=9, year=2023)
ANGLE_ORIGIN_DATE = datetime.date(day=21, month=6, year=2022 )
PIPS_ORIGIN_DATE = datetime.date(day=18, month=8, year=2025 )
KINDA_HARD_GOLF_ORIGIN_DATE = datetime.date(day=1, month=3, year=2025 )
CONNECTIONS_ORIGIN_DATE = datetime.date(day=11, month=6, year=2023 )
BANDLE_ORIGIN_DATE = datetime.date(day=17, month=8, year=2022 )
FIGURE_ORIGIN_DATE = datetime.date(day= 26, month=6, year=2022)
VIDEOPUZZLE_ORIGIN_DATE = datetime.date(day= 8, month=11, year=2024)
FLAGLE_ORIGIN_DATE = datetime.date(day= 14, month=3, year=2022)
FERMI_ESTIMATE_ORIGIN_DATE = datetime.date(day= 23, month=7, year=2025)
FOODGUESSR_ORIGIN_DATE = datetime.date(day= 22, month=7, year=2023)


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
    game: Mapped[str] = mapped_column(primary_key=True)
    date_of_game: Mapped[datetime.date]
    game_number: Mapped[int]
    timestamp: Mapped[datetime.datetime]



async def ingest_games_in_channel(ctx:discord.ApplicationContext):
    channel:discord.interactions.InteractionChannel = ctx.channel 
    async for msg in channel.history(limit=None):
        if msg.author.bot == True:
            continue
        await ingest_message(msg)

async def reingest_games_in_channel(ctx:discord.ApplicationContext):
    async with database.AsyncSessionLocal.begin() as session:
        channel:discord.interactions.InteractionChannel = ctx.channel 
        await session.execute(sqlalchemy.delete(Scores).where(Scores.channel_id == channel.id))
    await ingest_games_in_channel(ctx)


async def register_channel(ctx:discord.ApplicationContext):
    #sqlalchemy.exc.IntegrityError    
    async with database.AsyncSessionLocal.begin() as session:
        channel = RegisteredChannels()
        channel.channel_id = ctx.channel_id
        channel.timestamp_of_registration = discord.utils.utcnow()
        channel.who_registered_user_id = ctx.author.id

        session.add(channel)
    return

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
        channel = await session.get_one(RegisteredChannels, ctx.channel.id)
        await session.delete(channel)


async def in_registered_channel(message: discord.Message):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession
        result = await session.get(RegisteredChannels, message.channel.id)
        return result is not None
    

async def raw_game_data(game:str, user_id):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession

        result = []

        query = await session.execute(sqlalchemy.select(Scores).where(Scores.user_id == user_id).where(Scores.game == game).order_by(Scores.date_of_game.asc()))
        for score in query.scalars():
            result.append({"score":score.score, 
                           "date": score.date_of_game,
                           "gamenumber": score.game_number})

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

    functions_to_use = []
    games_to_use = []
    
    for pattern, (func, game) in registered_parsers.items():
        pattern: re.Pattern = pattern
        if pattern.search(contents) is not None:
            functions_to_use.append(func) 
            games_to_use.append(game)

  
    for function, game_name in zip(functions_to_use,games_to_use):
        parsed: tuple[int, datetime.date, int] | None = function(message)

        if parsed is None: # Happens when the parser cant parse the message, most likely cause the preliminary check isnt robust enough
            continue

        gamescore, gamedate, gamenumber = parsed
        await send_to_database(message=message, game_name=game_name, gamescore=gamescore, gamedate=gamedate, gamenumber=gamenumber )

           


async def send_to_database(message: discord.Message, game_name:str, gamescore: int, gamedate: datetime.date, gamenumber: int):
    async with database.AsyncSessionLocal.begin() as session:
        score = Scores(channel_id = message.channel.id,
                       game = game_name,
                       message_id = message.id,
                       user_id = message.author.id,
                       timestamp = message.created_at,
                       score = gamescore,
                       date_of_game = gamedate,
                       game_number=gamenumber)
        session.add(score)
        print(score)




def how_many_days_since_date(past_date: datetime.date, current_date: datetime.date):
    delta = current_date - past_date
    return delta.days


def date_after_days_passed(origin_date: datetime.date, days: int):
    days = int(days)
    return origin_date + datetime.timedelta(days=days)

@register_parser("Coindle", r"Coindle")
def coindle_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content


    date_match = re.search(r"Coindle (\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
    streak_match = re.search(r"Streak:\s*(\d+)", text)
    
    if date_match and streak_match:
        date_str = date_match.group(1)
        streak = int(streak_match.group(1))
        date_obj = datetime.date.fromisoformat(date_str)

        game_num = how_many_days_since_date(COINDLE_FIRST_GAME_DATE, date_obj)

        return streak, date_obj, game_num


@register_parser("Minigolfle", r"MINIGOLFLE #")
def minigolfle_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'^MINIGOLFLE\s+#(?P<game_number>\d+)[\r\n]+Strokes:\s*(?P<score>\d+)(?:[\r\n]+(?P<date>\d{4}-\d{2}-\d{2}))?',
        re.MULTILINE)
    data = pattern.search(text)
    if data is None:
        return
    
    result = data.groupdict()

    score = int(result["score"])
    game_number = int(result["game_number"])
    date = date_after_days_passed(MINIGOLFLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)


@register_parser("Syllacrostic", r"www.syllacrostic.com")
def syllacrostic_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'(?:(?P<title>[A-Z ]+)\s+)?#(?P<game_number>\d+)[\r\n]+[-\s]+[\r\n]+⏱️:\s*(?P<time>\d{2}:\d{2})(?:[\r\n]+[-\s]+)?(?:[\r\n]+(?P<date>\d{4}-\d{2}-\d{2}))?',
        re.MULTILINE)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    game_number = result["game_number"]

    time_string = result["time"]
    t = datetime.datetime.strptime(time_string, "%M:%S")
    delta = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    score = delta.total_seconds()

    date = date_after_days_passed(SYLLACROSTIC_ORIGIN_DATE , game_number)

    return float(score), date, int(game_number)

    

@register_parser("Catfishing", r"catfishing.net")
def catfishing_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'#(?P<game_number>\d+)\s*-\s*(?P<score>\d+(?:\.\d+)?)/(?P<max_score>\d+)',
        re.MULTILINE)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    game_number = result["game_number"]

    score = result["score"]

    date = date_after_days_passed(CATFISHING_ORIGIN_DATE , game_number)

    return float(score), date, int(game_number)


@register_parser("Timdle", r"TIMDLE")
def timdle_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'^(?P<game>TIMDLE)\s+(?P<date>[A-Za-z]+ \d+)[\r\n]+.?\s+(?P<score>\d+)/(?P<max_score>\d+)',
        re.MULTILINE)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = result["score"]

    date = datetime.datetime.strptime(f"{result["date"]} {message.created_at.year}", "%b %d %Y").date()

    game_number = how_many_days_since_date(TIMDLE_ORIGIN_DATE, date)

    return float(score), date, int(game_number)


@register_parser("Reunion", r"REUNION ")
def reunion_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'(?m)^(?P<game>REUNION)\s+(?P<date_str>[A-Za-z]+ \d{1,2}, \d{4})\s+.*?I solved it in (?P<moves>.*?) moves(?:\s+.*?(?P<url>https?://\S+))?',
        re.DOTALL)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()


    digits = re.findall(r'\d', result["moves"])
    score = int(''.join(digits))


    date = datetime.datetime.strptime(data['date_str'], "%B %d, %Y").date()

    game_number = how_many_days_since_date(REUNION_ORIGIN_DATE, date)


    return float(score), date, int(game_number)



@register_parser("Akari", r"Daily Akari")
def akari_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r'(?m)^(?P<game>Daily Akari)[^\n]*\n'
        r'(?P<weekday>[A-Za-z]{3})\s+(?P<month>[A-Za-z]{3})\s+(?P<day>\d{1,2}),\s+(?P<year>\d{4})\n'
        r'✅Solved in (?P<time>\d+:\d{2})✅\n'
        r'(?P<url>https?://\S+)',
        re.DOTALL)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    minutes, seconds = map(int, result['time'].split(':'))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    date = datetime.datetime.strptime(f"{result['month']} {result['day']} {result['year']}", "%b %d %Y").date()

    game_number = how_many_days_since_date(AKARI_ORIGIN_DATE, date)

    return float(score), date, int(game_number)




@register_parser("The Wiki Game Daily - Time", r"thewikigamedaily")
def wiki_game_daily_time_parser(message: discord.Message):
    

    text = message.content

    print(text)

    pattern = re.compile(
        r'⏰\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\D*?🦶\s*(?P<steps>\d+)',
        re.MULTILINE
    )

    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()


    minutes, seconds = map(int, result['time'].split(':'))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    date = message.created_at.date()

    game_number = how_many_days_since_date(WIKI_GAME_DAILY_ORIGIN_DATE, date)

    return float(score), date, int(game_number)



@register_parser("The Wiki Game Daily - Steps", r"thewikigamedail")
def wiki_game_daily_step_parser(message: discord.Message):


    text = message.content

    pattern = re.compile(
        r'⏰\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\D*?🦶\s*(?P<steps>\d+)',
        re.MULTILINE
    )
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = result["steps"]

    date = message.created_at.date()

    game_number = how_many_days_since_date(WIKI_GAME_DAILY_ORIGIN_DATE, date)

    return float(score), date, int(game_number)

@register_parser("Revealed", r"REVEALED: ")
def revealed_parser(message: discord.Message):
    text = message.content

    pattern = re.compile(
        r'(?m)^REVEALED:\s*(?P<date_str>[A-Za-z]+ \d{1,2}, \d{4})\s*.*?'
        r'(?:I solved it in\s*(?P<reveals_raw>[\d️⃣]+)\s*Reveals\s*&\s*(?P<hints_raw>[\d️⃣]+)\s*Hints|'
        r'I couldn’t solve it.*?)',
        re.DOTALL
)
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()



    def emoji_to_int(s):
        if not s:
            return None
        digits = re.findall(r'\d', s)
        return int(''.join(digits)) if digits else 0
    
    reveals = emoji_to_int(result['reveals_raw'])
    hints = emoji_to_int(result['hints_raw'])
    if reveals is None:
        score = 7 + 4 +1 # max reveal + max hints + 1
    else: 
        score = reveals + hints

    date = datetime.datetime.strptime(result['date_str'], "%b %d, %Y").date()

    game_number = how_many_days_since_date(REVEALED_ORIGIN_DATE, date)

    return float(score), date, int(game_number)

@register_parser("Wordle", r"Wordle")
def wiki_game_daily_step_parser(message: discord.Message):


    text = message.content

    pattern = re.compile(
        r'^Wordle\s+(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?',
        re.MULTILINE
    )

    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 7 


    game_number = int(result["number"].replace(',', ''))

    date = date_after_days_passed(WORDLE_ORIGIN_DATE,game_number)


    return float(score), date, int(game_number)


@register_parser("Costcodle", r"Costcodle")
def costcodle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^(?P<game>Costcodle)\s+#?(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?',
        re.MULTILINE
    )
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 7 
    game_number = int(result["number"].replace(',', ''))

    date = date_after_days_passed(COSTCODLE_ORIGIN_DATE,game_number)

    return float(score), date, int(game_number)



@register_parser("Angle", r"#Angle")
def angle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^#?(?P<game>Angle)\s+#?(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?',
        re.MULTILINE
    )
    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 5 
    game_number = int(result["number"].replace(',', ''))

    date = date_after_days_passed(ANGLE_ORIGIN_DATE,game_number)
    return float(score), date, int(game_number)


@register_parser("Pips - Hard", r"^Pips\s+#\d+\s+Hard")
@register_parser("Pips - Medium", r"^Pips\s+#\d+\s+Medium")
@register_parser("Pips - Easy", r"^Pips\s+#\d+\s+Easy")
def pips_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^Pips\s+#(?P<number>\d+)\s+(?P<difficulty>Hard|Medium|Easy).*?\n(?P<score>\d{1,2}:\d{2})',
        re.MULTILINE
    )

    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    minutes, seconds = map(int, result['score'].split(':'))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    game_number = int(result["number"])

    date = date_after_days_passed(PIPS_ORIGIN_DATE,game_number)

    #edge case because some people have wrong numbering by 1 day

    # if (date - message.created_at.date()).days == 1:
    #     game_number -= 1
    #     date = message.created_at.date()

    return float(score), date, int(game_number)


@register_parser("Kinda Hard Golf", r"kindahard.golf")
def kinda_hard_golf_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^kindahard\.golf\s+(?P<date>\d{1,2}/\d{1,2})'   
        r'(?:\s*\n+[\s📝]*(?P<total>\d+))?',              
        re.MULTILINE)

    
    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()


    score = result["total"]

    year = message.created_at.year

    month, day = map(int, result["date"].split('/'))
    date = datetime.date(year, month, day)


    game_number = how_many_days_since_date(KINDA_HARD_GOLF_ORIGIN_DATE, date)

    return float(score), date, int(game_number)


@register_parser("Connections", r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^(?P<game>Connections)\s*\nPuzzle\s*#(?P<number>\d+)',
        re.MULTILINE
    )


    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()


    grid_text = "\n".join(text.splitlines()[2:])

    # Regex for same-colored lines (all emojis identical)
    same_color_pattern = re.compile(r'^([🟦🟩🟨🟪🟧🟥🟫])\1*$', re.MULTILINE)
    # Regex for multicolored lines (at least 2 different emojis)
    multicolor_pattern = re.compile(r'^(?!([🟦🟩🟨🟪🟧🟥🟫])\1*$)[🟦🟩🟨🟪🟧🟥🟫]+$', re.MULTILINE)

    same_color_count = len(same_color_pattern.findall(grid_text))
    multicolor_count = len(multicolor_pattern.findall(grid_text))
    

    if multicolor_count == 4: # Player failed
        score = 5
    else: 

        score = multicolor_count

    game_number = int(result["number"])

    date = date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)


@register_parser("Bandle", r"Bandle #")
def bandle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
    r'^Bandle\s+#(?P<number>\d+)\s+(?P<score>[0-9x])/',
    re.MULTILINE)


    data = pattern.search(text)
    if data is None: 
        return
    result = data.groupdict()

    score = int(result["score"]) if result["score"].isdigit() else None

    if score is None:
        score = 7 

    game_number = int(result["number"].replace(',', ''))

    date = date_after_days_passed(BANDLE_ORIGIN_DATE,game_number)

    return float(score), date, int(game_number)


@register_parser("Figure", r"figure.game")
def figure_parser(message: discord.Message):

    text = message.content

    lines = text.strip().splitlines()
    if len(lines) < 4:
        return   

    # Game number: last number on line 2
    number_match = re.search(r'(\d+)\s*$', lines[1])
    game_number = int(number_match.group(1)) if number_match else None

    # Tries: first number on line 3
    tries_match = re.search(r'(\d+)', lines[2])
    tries = int(tries_match.group(1)) if tries_match else None

    # Hints: first number on line 4, 0 if "no hints" / "sin pistas" / missing
    hints_line = lines[3].strip().lower()
    hints_match = re.search(r'(\d+)', hints_line)
    hints = int(hints_match.group(1)) if hints_match else 0



    if game_number is None or tries is None: 
        return

    score = tries + hints


    date = date_after_days_passed(FIGURE_ORIGIN_DATE,game_number)

    return float(score), date, int(game_number)


@register_parser("Gisnep!", r"s #Gisnep in")
def gisnep_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
    r'in (?P<time>\d{1,2}:\d{2})\..*?\n'       
    r'No\.\s*(?P<number>\d+)\s*\|\s*(?P<date>.+?)\s*\n',         
    re.DOTALL
)


    data = pattern.search(text)

    if data is None: 
        return
    result = data.groupdict()
    minutes, seconds = map(int, result["time"].split(':'))
    score = minutes*60 + seconds


    game_number = int(result["number"].replace(',', ''))

    try:
        date = datetime.datetime.strptime(result["date"].strip(), '%B %d, %Y')  # Month Day, Year
    except ValueError:
        date = datetime.datetime.strptime(result["date"].strip(), '%d %B %Y')   # Day Month Year


    return float(score), date, int(game_number)



@register_parser("VideoPuzzle", r"VideoPuzzle.org")
def videopuzzle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'VideoPuzzle\.org\s+(?P<game_number>\d+)\s+\(Daily\).*?\n'  # game number
        r'(?:.*\n)*?'                                                 # skip any lines until Moves
        r'Moves:\s*(?P<moves>\d+)',                                   # moves line
        re.DOTALL
    )


    data = pattern.search(text)

    if data is None: 
        return
    
    result = data.groupdict()

    score = result["moves"]
    game_number = int(result["game_number"].replace(',', ''))

    date = date_after_days_passed(VIDEOPUZZLE_ORIGIN_DATE ,game_number)


    return float(score), date, int(game_number)


@register_parser("Flagle", r"flagle-game.com")
def flagle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'Flagle\s+#(?P<number>\d+)\s*-\s*(?P<score>\d|X)/6.*?\n',
        re.DOTALL
    )


    data = pattern.search(text)

    if data is None: 
        return
    result = data.groupdict()


    score = int(result["score"]) if result["score"].isdigit() else None
    if score is None:
        score = 7 

    game_number = int(result["number"].replace(',', ''))

    date = date_after_days_passed(FLAGLE_ORIGIN_DATE ,game_number)


    return float(score), date, int(game_number)

@register_parser("Fermi Estimate", r"https://fermiquestions.org/#")
def fermi_estimate_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'^(?:.*\n)*?'                               
        r'(?P<score_line>(?:[⬆️⬇️]+)?✅?)\s*\n'   
        r'(?P<url>https?://fermiquestions\.org/#/(?P<date>\d{4}-\d{2}-\d{2}))',
        re.MULTILINE
    )


    data = pattern.search(text)

    if data is None: 
        return
    result = data.groupdict()



    score = result["score_line"].count('⬆️') + result["score_line"].count('⬇️')


    date = datetime.datetime.strptime(result["date"], '%Y-%m-%d').date()

    game_number = how_many_days_since_date(FERMI_ESTIMATE_ORIGIN_DATE, date)



    return float(score), date, int(game_number)


@register_parser("Foodguessr", r"on the FoodGuessr Daily!")
def foodguessr_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r'I got (?P<total_score>[\d,]+) on the FoodGuessr Daily!.*?\n'  # total score
        r'(?:^(?!\w+, \w{3} \d{1,2}, \d{4}).*\n)*'                    # skip lines until a date line
        r'(?P<date>.+\d{1,2}, \d{4})\n',          
        re.MULTILINE | re.DOTALL
    )



    data = pattern.search(text)

    if data is None: 
        return
    result = data.groupdict()

    score = result["total_score"].replace(',', '')


    date = datetime.datetime.strptime(result["date"].strip(), '%A, %b %d, %Y').date()

    game_number = how_many_days_since_date(FOODGUESSR_ORIGIN_DATE, date)



    return float(score), date, int(game_number)




type User = discord.SlashCommandOptionType.user
async def generate_graph(game: str, player_1: User, player_2: User|None, player_3: User|None, player_4: User|None, dates_instead_of_numbers:bool):

    plt.figure(figsize=(6, 4))
    plt.title(f"{game} scores")
    plt.ylabel("Score")


    for index, player in enumerate([player_1,player_2,player_3,player_4]):

        if player is None:
            continue

        scores = await raw_game_data(game, player.id)

        if dates_instead_of_numbers:
            scores_x = [x["date"] for x in scores]
            plt.xlabel("Date")

        else:
            scores_x = [x["gamenumber"] for x in scores]
            plt.xlabel("Game number")

        scores_y = [x["score"] for x in scores]

        plt.plot(scores_x, scores_y, marker="o", label=f"{player.name}")

    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    plt.close()
    file = discord.File(buf, filename="score-history.png")
    return file
