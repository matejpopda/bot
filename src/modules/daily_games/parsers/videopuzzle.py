import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


VIDEOPUZZLE_ORIGIN_DATE = datetime.date(day=9, month=11, year=2024)
game_name = "VideoPuzzle"

game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Moves",
    url="https://videopuzzle.org/",
    description="Solve a video slide puzzle",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"VideoPuzzle\.org\s+(?P<game_number>\d+)\s+\(Daily\).*?\n"  # game number
    r"(?:.*\n)*?"  # skip any lines until Moves
    r"Moves:\s*(?P<moves>\d+)",  # moves line
    re.DOTALL,
)


@register_parser(game_name, r"VideoPuzzle.org")
def videopuzzle_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)

    if data is None:
        return

    result = data.groupdict()

    score = result["moves"]
    game_number = int(result["game_number"].replace(",", ""))

    date = utils.date_after_days_passed(VIDEOPUZZLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
