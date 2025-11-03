import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

KINDA_HARD_GOLF_ORIGIN_DATE = datetime.date(day=1, month=3, year=2025)






@register_parser("Kinda Hard Golf", r"kindahard.golf")
def kinda_hard_golf_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^kindahard\.golf\s+(?P<date>\d{1,2}/\d{1,2})"
        r"(?:\s*\n+[\s📝]*(?P<total>\d+))?",
        re.MULTILINE,
    )

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
