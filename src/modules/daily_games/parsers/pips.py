import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

PIPS_ORIGIN_DATE = datetime.date(day=18, month=8, year=2025)
easy_game_name = "Pips - Easy"
medium_game_name = "Pips - Medium"
hard_game_name = "Pips - Hard"


game_info = utils.GameInfo(
    game_name="Pips",
    fail_score=False,
    lower_score_is_better=True,
    score_name="Time taken",
    url="https://www.nytimes.com/games/pips",
    description="Place every domino in the right spot.",
)

add_game_info(easy_game_name, game_info)
add_game_info(medium_game_name, game_info)
add_game_info(hard_game_name, game_info)


pattern = re.compile(
    r"^Pips\s+#(?P<number>\d+)\s+(?P<difficulty>Hard|Medium|Easy).*?\n(?P<score>\d{1,2}:\d{2})",
    re.MULTILINE,
)


@register_parser(hard_game_name, r"^Pips\s+#\d+\s+Hard")
@register_parser(medium_game_name, r"^Pips\s+#\d+\s+Medium")
@register_parser(easy_game_name, r"^Pips\s+#\d+\s+Easy")
def pips_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    minutes, seconds = map(int, result["score"].split(":"))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    game_number = int(result["number"])

    date = utils.date_after_days_passed(PIPS_ORIGIN_DATE, game_number)

    # edge case because some people have wrong numbering by 1 day

    # if (date - message.created_at.date()).days == 1:
    #     game_number -= 1
    #     date = message.created_at.date()

    return float(score), date, int(game_number)
