import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

FOODGUESSR_ORIGIN_DATE = datetime.date(day=22, month=7, year=2023)
game_name = "Foodguessr"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=False,
    score_name="Points gained",
    url="https://www.foodguessr.com/",
    description="Guess where the dish is from.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"I got (?P<total_score>[\d,]+) on the FoodGuessr Daily!.*?\n"  # total score
    r"(?:^(?!\w+, \w{3} \d{1,2}, \d{4}).*\n)*"  # skip lines until a date line
    r"(?P<date>.+\d{1,2}, \d{4})\n",
    re.MULTILINE | re.DOTALL,
)


@register_parser(game_name, r"on the FoodGuessr Daily!")
def foodguessr_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)

    if data is None:
        return
    result = data.groupdict()

    score = result["total_score"].replace(",", "")

    date = datetime.datetime.strptime(result["date"].strip(), "%A, %b %d, %Y").date()

    game_number = utils.how_many_days_since_date(FOODGUESSR_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
