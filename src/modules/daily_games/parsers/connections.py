import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

import string

CONNECTIONS_ORIGIN_DATE = datetime.date(day=11, month=6, year=2023)
game_name = "Connections"



description = """ Find the 4 categories based on the connections between words.

Score is calculated as + 25% per correct answer - 10% per mistake. 
When you fail to guess you gain partial credit equal to 10% per correct answer. 

TLDR: Score of less than 60 was a failed game. 
"""

game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=60,
    lower_score_is_better=False,
    score_name="Score - Higher is better",
    url="https://www.nytimes.com/games/connections",
    description=description,
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^(?P<game>Connections)\s*\nPuzzle\s*#(?P<number>\d+)", re.MULTILINE
)

def calc_score(lines: list[str]):
    good_lines = 0
    bad_lines = 0
    
    def score_calc_helper(solved_lines: int, failed_lines:int):
        if failed_lines >= 4:
            return solved_lines * 10
        else:
            return 25* solved_lines - 10* failed_lines

    for line in lines:
        if not line:
            continue
        if len(line) != 4:
            continue

        if any(ch in string.ascii_lowercase for ch in line):
            continue
        
        if len(set(line)) > 1: # converting to set to find out if its unique
            bad_lines += 1
        else:
            good_lines += 1

    return score_calc_helper(good_lines, bad_lines)

@register_parser(game_name, r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()



    score = calc_score(text.splitlines()[2:])


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


    score = calc_score(text.splitlines()[1:])
    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return score, date, game_number
