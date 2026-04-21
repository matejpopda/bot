import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info


NONODAILY_ORIGIN_DATE = datetime.date(day=23, month=2, year=2026)
game_name = "NonoDaily"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Seconds",
    url="https://nonodaily.com/",
    description="Fill the nonogram :)",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"(?m)^.*NonoDaily.*\n"
    r"🗓️\s*(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?,\s+(?P<year>\d{4})\n"
    r"⏱️\s*(?P<time>\d{1,2}:\d{2})\n"
)


@register_parser(game_name, r"NonoDaily")
def nonodaily_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    clean_day = re.sub(r"(st|nd|rd|th)", "", result["day"])

    date = datetime.datetime.strptime(
        f"{result['month']} {clean_day} {result['year']}",
        "%b %d %Y"
    ).date()

    hours, minutes = map(int, result["time"].split(":"))
    seconds = hours * 60 + minutes

    game_number = utils.how_many_days_since_date(NONODAILY_ORIGIN_DATE, date)

    return float(seconds), date, int(game_number)
