import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

COSTCODLE_ORIGIN_DATE = datetime.date(day=19, month=9, year=2023)
game_name = "Costcodle"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=7,
    lower_score_is_better=True,
    score_name="Number of guesses",
    url="https://costcodle.com/",
    description="Guess the price of an item from Costco",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^(?P<game>Costcodle)\s+#?(?P<number>[\d,]+)\s+(?P<guesses>[\dX]+)(?:/\d+|/∞)?",
    re.MULTILINE,
)


@register_parser(game_name, r"Costcodle")
def costcodle_parser(message: discord.Message):

    text = message.content

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
