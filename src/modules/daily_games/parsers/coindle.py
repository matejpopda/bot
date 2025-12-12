import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

COINDLE_FIRST_GAME_DATE = datetime.date(year=2025, month=10, day=8)
game_name = "Coindle"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=0
                            ,lower_score_is_better=False
                            ,score_name="Guessed flips"
                            ,url="https://muhashi.com/coindle/"
                            ,description="Get as many coin flips correct in a row."
                            )

add_game_info(game_name, game_info)




pattern = re.compile(
    r'Coindle\s+(?P<date>\d{4}-\d{1,2}-\d{1,2})\s*?\n'
    r'Streak:\s*(?P<streak>\d+)', 
    re.MULTILINE
)


@register_parser(game_name, r"Coindle")
def coindle_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content


    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    score = int(result['streak'])
    date = datetime.datetime.strptime(result['date'], '%Y-%m-%d').date()
    game_number = utils.how_many_days_since_date(COINDLE_FIRST_GAME_DATE, date)


    return score, date, game_number
