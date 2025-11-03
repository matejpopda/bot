import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

CATFISHING_ORIGIN_DATE = datetime.date(day=23, month=6, year=2024)

@register_parser("Catfishing", r"catfishing.net")
def catfishing_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r"#(?P<game_number>\d+)\s*-\s*(?P<score>\d+(?:\.\d+)?)/(?P<max_score>\d+)",
        re.MULTILINE,
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    game_number = result["game_number"]

    score = result["score"]

    date = utils.date_after_days_passed(CATFISHING_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)

