import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


MINIGOLFLE_ORIGIN_DATE = datetime.date(day=29, month=9, year=2025)
game_name = "Minigolfle"

game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Number of shots",
    url="https://minigolfle.com/",
    description="Play minigolf.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^MINIGOLFLE\s+#(?P<game_number>\d+)[\r\n]+Strokes:\s*(?P<score>\d+)(?:[\r\n]+(?P<date>\d{4}-\d{2}-\d{2}))?",
    re.MULTILINE,
)


@register_parser(game_name, r"MINIGOLFLE #")
def minigolfle_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    score = int(result["score"])
    game_number = int(result["game_number"])
    date = utils.date_after_days_passed(MINIGOLFLE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
