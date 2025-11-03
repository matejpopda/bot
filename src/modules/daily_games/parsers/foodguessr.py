import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

FOODGUESSR_ORIGIN_DATE = datetime.date(day=22, month=7, year=2023)

pattern = re.compile(
    r"I got (?P<total_score>[\d,]+) on the FoodGuessr Daily!.*?\n"  # total score
    r"(?:^(?!\w+, \w{3} \d{1,2}, \d{4}).*\n)*"  # skip lines until a date line
    r"(?P<date>.+\d{1,2}, \d{4})\n",
    re.MULTILINE | re.DOTALL,
)



@register_parser("Foodguessr", r"on the FoodGuessr Daily!")
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
