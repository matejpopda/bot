import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

FIGURE_ORIGIN_DATE = datetime.date(day=26, month=6, year=2022)
game_name = "Figure"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=None
                            ,lower_score_is_better=True
                            ,score_name="Number of tries" 
                            ,url="https://figure.game/"
                            ,description="Puzzle game where you need to clear the gameboard."
                            )

add_game_info(game_name, game_info)





@register_parser(game_name, r"figure.game")
def figure_parser(message: discord.Message):

    text = message.content

    lines = text.strip().splitlines()
    if len(lines) < 4:
        return

    # Game number: last number on line 2
    number_match = re.search(r"(\d+)\s*$", lines[1])
    game_number = int(number_match.group(1)) if number_match else None

    # Tries: first number on line 3
    tries_match = re.search(r"(\d+)", lines[2])
    tries = int(tries_match.group(1)) if tries_match else None

    # Hints: first number on line 4, 0 if "no hints" / "sin pistas" / missing
    hints_line = lines[3].strip().lower()
    hints_match = re.search(r"(\d+)", hints_line)
    hints = int(hints_match.group(1)) if hints_match else 0

    if game_number is None or tries is None:
        return

    score = tries + hints

    date = utils.date_after_days_passed(FIGURE_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
