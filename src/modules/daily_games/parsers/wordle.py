import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

WORDLE_ORIGIN_DATE = datetime.date(day=19, month=6, year=2021)




pattern = re.compile(
    r"^Wordle\s+(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?", re.MULTILINE
)


@register_parser("Wordle", r"Wordle")
def wiki_game_daily_step_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = int(result["guesses"]) if result["guesses"].isdigit() else None

    if score is None:
        score = 7

    game_number = int(result["number"].replace(",", ""))

    date = utils.date_after_days_passed(WORDLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)