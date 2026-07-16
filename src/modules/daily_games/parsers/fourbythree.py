import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser, register_link_association_for_automatic_link_posting
from ..daily_games import add_game_info

FOUR_BY_THREE_ORIGIN_DATE = datetime.date(day=24, month=6, year=2026)
game_name = "4x3"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=0,
    lower_score_is_better=False,
    score_name="Score",
    url="https://www.hankgreen.com/fourbythree",
    description="Find the categories.",
)

add_game_info(game_name, game_info)

# register_link_association_for_automatic_link_posting("4x3.fun", ("https://www.hankgreen.com/fourbythree", "https://4x3.fun/"))

pattern = re.compile(
    r"(?P<date>\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+((?P<score>\d+)\s+points|Out of guesses)"
)



@register_parser(game_name, r"4x3.fun")
@register_parser(game_name, r"https://4x3.fun/")
def fourbythree_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()


    score = result["score"]

    if score is None:
        score = 0

    date = datetime.datetime.strptime(result["date"], "%d %B %Y").date()

    game_number = utils.how_many_days_since_date(FOUR_BY_THREE_ORIGIN_DATE, date)

    return float(score), date, game_number

