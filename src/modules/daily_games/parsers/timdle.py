import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser



TIMDLE_ORIGIN_DATE = datetime.date(
    day=26, month=1, year=2025
)  # Based on wayback machine its somewhere between december 2024 and this date


@register_parser("Timdle", r"TIMDLE")
def timdle_parser(message: discord.Message):

    text = message.content

    pattern = re.compile(
        r"^(?P<game>TIMDLE)\s+(?P<date>[A-Za-z]+ \d+)[\r\n]+.?\s+(?P<score>\d+)/(?P<max_score>\d+)",
        re.MULTILINE,
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = result["score"]

    date = datetime.datetime.strptime(
        f"{result["date"]} {message.created_at.year}", "%b %d %Y"
    ).date()

    game_number = utils.how_many_days_since_date(TIMDLE_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
