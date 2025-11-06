import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

WIKI_GAME_DAILY_ORIGIN_DATE = datetime.date(
    day=17, month=7, year=2024
)  # Based on wayback machine
time_game_name = "The Wiki Game Daily - Time"
step_game_name = "The Wiki Game Daily - Steps"


time_game_info = utils.GameInfo(
    game_name=time_game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Seconds taken",
    url="https://www.thewikigamedaily.com/",
    description="Find the path between two Wikipedia articles as fast as possible",
)

add_game_info(time_game_name, time_game_info)


step_game_info = utils.GameInfo(
    game_name=step_game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Steps taken",
    url="https://www.thewikigamedaily.com/",
    description="Find the path between two Wikipedia articles in fewest steps possible",
)

add_game_info(step_game_name, step_game_info)


pattern = re.compile(
    r"⏰\s*(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\D*?🦶\s*(?P<steps>\d+)", re.MULTILINE
)


@register_parser(time_game_name, r"thewikigamedaily")
def wiki_game_daily_time_parser(message: discord.Message):

    text = message.content

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

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = result["steps"]

    date = message.created_at.date()

    game_number = utils.how_many_days_since_date(WIKI_GAME_DAILY_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
