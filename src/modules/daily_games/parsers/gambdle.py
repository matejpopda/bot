import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

GAMBDLE_ORIGIN_DATE = datetime.date(day=5, month=5, year=2026)
game_name = "Gambdle"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=0,
    lower_score_is_better=False,
    score_name="Chips",
    url="https://gambdle.net/",
    description="Gamble!",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"🎰\s*Gambdle\s*#(?P<game_number>\d+).*?Finished with\s+(?P<chips>[\d,]+)\s+chips",
    re.DOTALL,
)

@register_parser(game_name, r"Gambdle #")
def gambdleparser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    game_number = int(result["game_number"])

    score = result["chips"].replace(",", "")

    date = utils.date_after_days_passed(GAMBDLE_ORIGIN_DATE, game_number)

    return float(score), date, game_number
