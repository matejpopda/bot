import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

ANGLE_ORIGIN_DATE = datetime.date(day=21, month=6, year=2022)






@register_parser("Angle", r"#Angle")
def angle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^#?(?P<game>Angle)\s+#?(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?",
        re.MULTILINE,
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 5
    game_number = int(result["number"].replace(",", ""))

    date = utils.date_after_days_passed(ANGLE_ORIGIN_DATE, game_number)
    return float(score), date, int(game_number)