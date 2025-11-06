import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

KINDA_HARD_GOLF_ORIGIN_DATE = datetime.date(day=1, month=3, year=2025)
game_name = "Kinda Hard Golf"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Number of shots",
    url="https://kindahardgolf.com/",
    description="Play golf, its kinda hard.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^kindahard\.golf\s+(?P<date>\d{1,2}/\d{1,2})" r"(?:\s*\n+[\s📝]*(?P<total>\d+))?",
    re.MULTILINE,
)


@register_parser(game_name, r"kindahard.golf")
def kinda_hard_golf_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = result["total"]

    year = message.created_at.year

    month, day = map(int, result["date"].split("/"))
    date = datetime.date(year, month, day)

    game_number = utils.how_many_days_since_date(KINDA_HARD_GOLF_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
