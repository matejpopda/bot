import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

CHARTLE_ORIGIN_DATE = datetime.date(day=10, month=9, year=2025)
game_name = "Chartle"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=5,
    lower_score_is_better=True,
    score_name="Number of guesses",
    url="https://chartle.cc/",
    description="Guess the country based on the chart.",
)

add_game_info(game_name, game_info)


pattern  = re.compile(
    r'^📈\s*Chartle\s+for\s+(?P<date>\d{1,2}\s+\w+\s+\d{4}):\s+(?P<title>.+?)\r?\n\r?\n'
    r'(?:Failed to guess this time|Guessed in\s+(?P<tries>\d+)\s+tries)',
    re.MULTILINE
)


@register_parser(game_name, r"📈\s*Chartle\b")
def chartle_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()


    date = datetime.datetime.strptime(data["date"], "%d %b %Y").date()

    score: int = int(result["tries"]) if result["tries"] else 6

    game_number = utils.how_many_days_since_date(CHARTLE_ORIGIN_DATE, date)

    return score, date, game_number
