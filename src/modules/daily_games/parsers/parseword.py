import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


PARSEWORD_ORIGIN_DATE = datetime.date(day=28, month=1, year=2026)
game_name = "Parseword"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Seconds",
    url="https://www.parseword.com/",
    description="Solve a cryptogram. 30 second penalty in the scoring for hints.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"Parseword\s+#(?P<id>\d+).*?"
    r"(?:(?P<min>\d+)m)?(?P<sec>\d+)s.*?"
    r"(?:(?P<hints>\d+)\s*Hints?)?",
    re.DOTALL
)


@register_parser(game_name, r"Parseword")
def parseword_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    if result["min"]:
        score = int(result["min"]) * 60 + int(result["sec"])
    else:
        score = int(result["sec"])


    if result["hints"] is not None:
        score += int(result["hints"])*30

    game_number = int(result["id"])
    
    date = utils.date_after_days_passed(PARSEWORD_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
