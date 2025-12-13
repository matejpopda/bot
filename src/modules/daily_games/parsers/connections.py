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

def count_mixed_lines(lines):
    count = 0
        
    for line in lines:
        if not line:
            continue
        if len(line) != 4:
            continue

        if any(ch not in string.ascii_lowercase for ch in line):
            continue
        
        if len(set(line)) > 1: # converting to set to find out if its unique
            count += 1
    return count

@register_parser(game_name, r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()



    score = count_mixed_lines(text.splitlines()[2:])

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


    score = count_mixed_lines(text.splitlines()[1:])
    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return score, date, game_number
