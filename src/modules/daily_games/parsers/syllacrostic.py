import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

SYLLACROSTIC_ORIGIN_DATE = datetime.date(day=28, month=3, year=2023)
game_name = "Syllacrostic"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Time taken",
    url="https://www.syllacrostic.com/",
    description="Solve crossword like clues by combining syllables.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"(?:(?P<title>[A-Z ]+)\s+)?#(?P<game_number>\d+)[\r\n]+[-\s]+[\r\n]+⏱️:\s*(?P<time>\d{2}:\d{2})(?:[\r\n]+[-\s]+)?(?:[\r\n]+(?P<date>\d{4}-\d{2}-\d{2}))?",
    re.MULTILINE,
)


@register_parser(game_name, r"https://syllacrostic.com/")
@register_parser(game_name, r"www.syllacrostic.com")
def syllacrostic_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    game_number = result["game_number"]

    time_string = result["time"]
    t = datetime.datetime.strptime(time_string, "%M:%S")
    delta = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    score = delta.total_seconds()

    date = utils.date_after_days_passed(SYLLACROSTIC_ORIGIN_DATE, game_number)

    return float(score), date, int(game_number)
