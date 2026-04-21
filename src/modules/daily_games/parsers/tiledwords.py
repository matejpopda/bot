import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


TILED_WORDS_ORIGIN_DATE = datetime.date(day=19, month=10, year=2025)
game_name = "Tiled Words"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Seconds",
    url="https://tiledwords.com/",
    description="Build a crossword",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"I solved today's #TiledWords puzzle!\s*"
    r"(?:\n.*?)*?"
    r"[^\w\s]?\s*“(?P<word>.+?)”\s*\n"
    r"🕒\s*(?P<minutes>\d+)\s*minutes?,\s*(?P<seconds>\d+)\s*seconds?\s*\n"
    r"(?:💡.*\n)?"
    r"(?P<url>https?://\S+/puzzles/(?P<date>\d{4}-\d{2}-\d{2}))",
    re.DOTALL
)


@register_parser(game_name, r"#TiledWords")
def tiled_words_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    minutes, seconds = int(result["minutes"]), int(result["seconds"])
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    date = datetime.date.fromisoformat(result["date"])
    game_number = utils.how_many_days_since_date(TILED_WORDS_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
