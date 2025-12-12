import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

SCRANDLE_FIRST_GAME_DATE = datetime.date(year=2025, month=4, day=19)
game_name = "Scrandle"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=0
                            ,lower_score_is_better=False
                            ,score_name="Correct guesses"
                            ,url="https://scrandle.com/"
                            ,description="Guess which scran is superior."
                            )

add_game_info(game_name, game_info)




pattern = re.compile(
    r'(?P<grid>[🟩🟥⬛]+)\s+(?P<score>\d+)/10\s+\|\s+(?P<date>\d{4}-\d{2}-\d{2})',
    re.MULTILINE
)



@register_parser(game_name, r"scrandle\.com")
def scrandle_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content


    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    score = int(result['score'])
    date = datetime.datetime.strptime(result['date'], "%Y-%m-%d").date()
    game_number = utils.how_many_days_since_date(SCRANDLE_FIRST_GAME_DATE, date)


    return score, date, game_number
