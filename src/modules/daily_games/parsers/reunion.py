import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

REUNION_ORIGIN_DATE = datetime.date(day=8, month=10, year=2025)
game_name = "Reunion"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Number of moves",
    url="www.merriam-webster.com/games/reunion",
    description="Solve a crossword by permuting letters.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"(?m)^(?P<game>REUNION)\s+(?P<date_str>[A-Za-z]+ \d{1,2}, \d{4})\s+.*?I solved it in (?P<moves>.*?) moves(?:\s+.*?(?P<url>https?://\S+))?",
    re.DOTALL,
)


@register_parser(game_name, r"REUNION ")
def reunion_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    digits = re.findall(r"\d", result["moves"])
    score = int("".join(digits))

    date = datetime.datetime.strptime(data["date_str"], "%B %d, %Y").date()

    game_number = utils.how_many_days_since_date(REUNION_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
