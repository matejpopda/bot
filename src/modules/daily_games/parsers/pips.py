import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

PIPS_ORIGIN_DATE = datetime.date(day=18, month=8, year=2025)




@register_parser("Pips - Hard", r"^Pips\s+#\d+\s+Hard")
@register_parser("Pips - Medium", r"^Pips\s+#\d+\s+Medium")
@register_parser("Pips - Easy", r"^Pips\s+#\d+\s+Easy")
def pips_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^Pips\s+#(?P<number>\d+)\s+(?P<difficulty>Hard|Medium|Easy).*?\n(?P<score>\d{1,2}:\d{2})",
        re.MULTILINE,
    )

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