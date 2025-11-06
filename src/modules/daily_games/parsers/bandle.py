import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

BANDLE_ORIGIN_DATE = datetime.date(day=17, month=8, year=2022)
game_name = "Bandle"

game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=7,
    lower_score_is_better=True,
    score_name="Number of guesses",
    url="https://bandle.app/",
    description="Guess the song 1 instrument at a time",
)

add_game_info(game_name, game_info)


pattern = re.compile(r"^Bandle\s+#(?P<number>\d+)\s+(?P<score>[0-9x])/", re.MULTILINE)


@register_parser(game_name, r"Bandle #")
def bandle_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    score = int(result["score"]) if result["score"].isdigit() else None

    if score is None:
        score = 7

    game_number = int(result["number"].replace(",", ""))

    date = utils.date_after_days_passed(BANDLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
