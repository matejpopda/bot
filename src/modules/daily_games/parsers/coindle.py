import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

COINDLE_FIRST_GAME_DATE = datetime.date(year=2025, month=10, day=8)



@register_parser("Coindle", r"Coindle")
def coindle_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content

    pattern = re.compile(
        r'Coindle\s+(?P<date>\d{4}-\d{1,2}-\d{1,2})\s*?\n'
        r'Streak:\s*(?P<streak>\d+)', 
        re.MULTILINE
    )
    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    score = int(result['streak'])
    date = datetime.datetime.strptime(result['date'], '%Y-%m-%d').date()
    game_number = utils.how_many_days_since_date(COINDLE_FIRST_GAME_DATE, date)


    return float(score), date, int(game_number)
