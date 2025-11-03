import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

WIKI_GAME_DAILY_ORIGIN_DATE = datetime.date(
    day=17, month=7, year=2024
)  # Based on wayback machine

@register_parser("The Wiki Game Daily - Time", r"thewikigamedaily")
def wiki_game_daily_time_parser(message: discord.Message):

    text = message.content


    pattern = re.compile(
        r"⏰\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\D*?🦶\s*(?P<steps>\d+)", re.MULTILINE
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    minutes, seconds = map(int, result["time"].split(":"))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    date = message.created_at.date()

    game_number = utils.how_many_days_since_date(WIKI_GAME_DAILY_ORIGIN_DATE, date)

    return float(score), date, int(game_number)


@register_parser("The Wiki Game Daily - Steps", r"thewikigamedail")
def wiki_game_daily_step_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r"⏰\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\D*?🦶\s*(?P<steps>\d+)", re.MULTILINE
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = result["steps"]

    date = message.created_at.date()

    game_number = utils.how_many_days_since_date(WIKI_GAME_DAILY_ORIGIN_DATE, date)

    return float(score), date, int(game_number)

