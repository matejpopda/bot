import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser




@register_parser("Gisnep!", r"s #Gisnep in")
def gisnep_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"in (?P<time>\d{1,2}:\d{2})\..*?\n"
        r"No\.\s*(?P<number>\d+)\s*\|\s*(?P<date>.+?)\s*\n",
        re.DOTALL,
    )

    data = pattern.search(text)

    if data is None:
        return
    result = data.groupdict()
    minutes, seconds = map(int, result["time"].split(":"))
    score = minutes * 60 + seconds

    game_number = int(result["number"].replace(",", ""))

    try:
        date = datetime.datetime.strptime(
            result["date"].strip(), "%B %d, %Y"
        )  # Month Day, Year
    except ValueError:
        date = datetime.datetime.strptime(
            result["date"].strip(), "%d %B %Y"
        )  # Day Month Year

    return float(score), date, int(game_number)
