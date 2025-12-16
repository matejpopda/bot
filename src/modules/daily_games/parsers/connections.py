import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

import string

CONNECTIONS_ORIGIN_DATE = datetime.date(day=11, month=6, year=2023)
game_name = "Connections"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=4,
    lower_score_is_better=True,
    score_name="Failed guesses",
    url="https://www.nytimes.com/games/connections",
    description="Find the 4 categories based on the connections between words.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^(?P<game>Connections)\s*\nPuzzle\s*#(?P<number>\d+)", re.MULTILINE
)

def score(lines: list[str]):
    good_lines = 0
    bad_lines = 0
    
    def score_calc(solved_lines: int, failed_lines:int):
        if failed_lines >= 4:
            return solved_lines * 10
        else:
            return 25* solved_lines - 10* failed_lines

    for line in lines:
        if not line:
            continue
        if len(line) != 4:
            continue

        if any(ch not in string.ascii_lowercase for ch in line):
            continue
        
        if len(set(line)) > 1: # converting to set to find out if its unique
            bad_lines += 1
        else:
            good_lines += 1
    return score_calc(good_lines, bad_lines)

@register_parser(game_name, r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()



    score = score(text.splitlines()[2:])

    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return score, date, game_number





pattern_infinite = re.compile(
    r"^(?P<game>Connections)\s*#(?P<number>\d+)", re.MULTILINE
)


@register_parser(game_name, r"^Connections ")
def connections_parser_2(message: discord.Message):

    text = message.content

    data = pattern_infinite.search(text)
    if data is None:
        return
    result = data.groupdict()


    score = score(text.splitlines()[1:])
    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return score, date, game_number
