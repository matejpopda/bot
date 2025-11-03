import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

COSTCODLE_ORIGIN_DATE = datetime.date(day=19, month=9, year=2023)



@register_parser("Costcodle", r"Costcodle")
def costcodle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^(?P<game>Costcodle)\s+#?(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?",
        re.MULTILINE,
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 7
    game_number = int(result["number"].replace(",", ""))

    date = utils.date_after_days_passed(COSTCODLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
