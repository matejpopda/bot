import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

DECODEX_FIRST_GAME_DATE = datetime.date(year=2024, month=12, day=1)
game_name = "Decodex"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=None
                            ,lower_score_is_better=True
                            ,score_name="Time taken"
                            ,url="https://www.playdecodex.com/"
                            ,description="Decrypt the encoded quote by guessing the correct letter for each encoded character."
                            )

add_game_info(game_name, game_info)


pattern = re.compile(
    r"Decodex\s+(?P<date>\d{4}-\d{2}-\d{2})\s*[\s\S]*?Time:\s*(?P<time>\d{1,2}:\d{2})",
    re.MULTILINE
)

@register_parser(game_name, r"^Decodex")
def decodex_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content


    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    minutes, seconds = map(int, result["time"].split(":"))
    score = minutes * 60 + seconds


    date = datetime.datetime.strptime(result['date'], "%Y-%m-%d").date()
    game_number = utils.how_many_days_since_date(DECODEX_FIRST_GAME_DATE, date)

    return float(score), date, int(game_number)
