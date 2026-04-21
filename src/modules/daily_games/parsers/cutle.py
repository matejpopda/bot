import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


CUTLE_ORIGIN_DATE = datetime.date(day=23, month=11, year=2025)
game_name = "Cutle"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=False,
    score_name="Percentage %",
    url="https://pfiffel.com/cutle",
    description="Cut the shape in half",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"Cutle\s+#(?P<id>\d+):\s*"
    r".*?\s*(?P<percent>\d+:\d{2})\s*.*?\s*"
    r"\((?P<date>\d{4}-\d{2}-\d{2})\)\s*-\s*"
    r"(?P<url>https?://\S+)"
)


@register_parser(game_name, r"Cutle ")
def cutle_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    up, bellow = map(int, result["percent"].split(":"))
    score = min(up, bellow) * 2 

    date = datetime.date.fromisoformat(result["date"])

    game_number = utils.how_many_days_since_date(CUTLE_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
