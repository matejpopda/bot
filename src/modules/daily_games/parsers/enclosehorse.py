import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


ENCLOSE_HORSE_ORIGIN_DATE = datetime.date(day=29, month=12, year=2025)
game_name = "Enclose.horse"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=False,
    score_name="Percent %",
    url="https://enclose.horse/",
    description="Enclose horse in the biggest area",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"(?:https?://)?enclose\.horse/?\s+Day\s+(?P<day>\d+).*?(?P<percent>\d+)%",
    re.DOTALL
)

@register_parser(game_name, r"enclose.horse")
def enclose_horse_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return

    
    score = int(data.group("percent"))  



    game_number = int(data.group("day")) 
    date = utils.date_after_days_passed(ENCLOSE_HORSE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
