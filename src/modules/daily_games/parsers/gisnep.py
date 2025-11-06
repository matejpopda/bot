import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

game_name = "Gisnep!"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=None,
    lower_score_is_better=True,
    score_name="Time",
    url="https://gisnep.com/",
    description="Figure out the quote based on few rules.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"in (?P<time>\d{1,2}:\d{2})\..*?\n"
    r"No\.\s*(?P<number>\d+)\s*\|\s*(?P<date>.+?)\s*\n",
    re.DOTALL,
)


@register_parser(game_name, r"s #Gisnep in")
def gisnep_parser(message: discord.Message):

    text = message.content

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
