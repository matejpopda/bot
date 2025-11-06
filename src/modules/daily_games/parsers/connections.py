import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

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
# Regex for same-colored lines (all emojis identical)
same_color_pattern = re.compile(r"^([🟦🟩🟨🟪🟧🟥🟫])\1*$", re.MULTILINE)
# Regex for multicolored lines (at least 2 different emojis)
multicolor_pattern = re.compile(
    r"^(?!([🟦🟩🟨🟪🟧🟥🟫])\1*$)[🟦🟩🟨🟪🟧🟥🟫]+$", re.MULTILINE
)


@register_parser(game_name, r"^Connections")
def connections_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    grid_text = "\n".join(text.splitlines()[2:])

    same_color_count = len(same_color_pattern.findall(grid_text))
    multicolor_count = len(multicolor_pattern.findall(grid_text))

    score = multicolor_count

    game_number = int(result["number"])

    date = utils.date_after_days_passed(CONNECTIONS_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
