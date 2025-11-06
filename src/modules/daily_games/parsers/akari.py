import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


AKARI_ORIGIN_DATE = datetime.date(day=5, month=1, year=2025)
game_name = "Akari"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Seconds",
    url="https://dailyakari.com/",
    description="Just make the blocks happy :)",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"(?m)^(?P<game>Daily Akari)[^\n]*\n"
    r"(?P<weekday>[A-Za-z]{3})\s+(?P<month>[A-Za-z]{3})\s+(?P<day>\d{1,2}),\s+(?P<year>\d{4})\n"
    r"✅Solved in (?P<time>\d+:\d{2})✅\n"
    r"(?P<url>https?://\S+)",
    re.DOTALL,
)


@register_parser(game_name, r"Daily Akari")
def akari_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    minutes, seconds = map(int, result["time"].split(":"))
    score = datetime.timedelta(minutes=minutes, seconds=seconds).seconds

    date = datetime.datetime.strptime(
        f"{result['month']} {result['day']} {result['year']}", "%b %d %Y"
    ).date()

    game_number = utils.how_many_days_since_date(AKARI_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
