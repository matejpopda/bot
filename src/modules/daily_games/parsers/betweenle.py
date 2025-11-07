import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

BETWEENLE_FIRST_GAME_DATE = datetime.date(year=2023, month=3, day=16)
game_name = "Betweenle"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=0
                            ,lower_score_is_better=False
                            ,score_name="Score"
                            ,url="https://betweenle.com/"
                            ,description="Find the word in a dictionary."
                            )

add_game_info(game_name, game_info)


pattern = re.compile(
    r"Betweenle\s+(?P<game_number>\d+)\s*-\s*(?P<score>\d+)",
    re.IGNORECASE
)

@register_parser(game_name, r"^Betweenle")
def betweenle_parser(message: discord.Message) -> tuple[int, datetime.date, int] | None:

    text = message.content


    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    score = result["score"]

    game_number = result["game_number"]

    date = utils.date_after_days_passed(BETWEENLE_FIRST_GAME_DATE, game_number)


    return float(score), date, int(game_number)
