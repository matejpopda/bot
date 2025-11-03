import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

CONNECTIONS_ORIGIN_DATE = datetime.date(day=11, month=6, year=2023)




@register_parser("Connections", r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^(?P<game>Connections)\s*\nPuzzle\s*#(?P<number>\d+)", re.MULTILINE
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    grid_text = "\n".join(text.splitlines()[2:])

    # Regex for same-colored lines (all emojis identical)
    same_color_pattern = re.compile(r"^([🟦🟩🟨🟪🟧🟥🟫])\1*$", re.MULTILINE)
    # Regex for multicolored lines (at least 2 different emojis)
    multicolor_pattern = re.compile(
        r"^(?!([🟦🟩🟨🟪🟧🟥🟫])\1*$)[🟦🟩🟨🟪🟧🟥🟫]+$", re.MULTILINE
    )

    same_color_count = len(same_color_pattern.findall(grid_text))
    multicolor_count = len(multicolor_pattern.findall(grid_text))

    if multicolor_count == 4:  # Player failed
        score = 5
    else:

        score = multicolor_count

    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
