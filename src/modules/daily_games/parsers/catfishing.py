import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

CATFISHING_ORIGIN_DATE = datetime.date(day=23, month=6, year=2024)
game_name = "Catfishing"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=0,
    lower_score_is_better=False,
    score_name="Correct guesses",
    url="https://catfishing.net/",
    description="Guess the Wikipedia article from its categories.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"#(?P<game_number>\d+)\s*-\s*(?P<score>\d+(?:\.\d+)?)/(?P<max_score>\d+)",
    re.MULTILINE,
)


@register_parser(game_name, r"catfishing.net")
def catfishing_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    game_number = int(result["game_number"])

    score = result["score"]

    date = utils.date_after_days_passed(CATFISHING_ORIGIN_DATE, game_number)

    return float(score), date, game_number
