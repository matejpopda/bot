import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser



VIDEOPUZZLE_ORIGIN_DATE = datetime.date(day=8, month=11, year=2024)


@register_parser("VideoPuzzle", r"VideoPuzzle.org")
def videopuzzle_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"VideoPuzzle\.org\s+(?P<game_number>\d+)\s+\(Daily\).*?\n"  # game number
        r"(?:.*\n)*?"  # skip any lines until Moves
        r"Moves:\s*(?P<moves>\d+)",  # moves line
        re.DOTALL,
    )

    data = pattern.search(text)

    if data is None:
        return

    result = data.groupdict()

    score = result["moves"]
    game_number = int(result["game_number"].replace(",", ""))

    date = utils.date_after_days_passed(VIDEOPUZZLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
