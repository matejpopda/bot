import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

FERMI_ESTIMATE_ORIGIN_DATE = datetime.date(day=23, month=7, year=2025)
game_name = "Fermi Estimate"


game_info = utils.GameInfo(
    game_name=game_name,
    fail_score=6,
    lower_score_is_better=True,
    score_name="Number of guesses",
    url="https://www.fermiquestions.org",
    description="Guess the answer to an estimation question.",
)

add_game_info(game_name, game_info)


pattern = re.compile(
    r"^(?:.*\n)*?"
    r"(?P<score_line>(?:[⬆️⬇️]+)?✅?)\s*\n"
    r"(?P<url>https?://fermiquestions\.org/#/(?P<date>\d{4}-\d{2}-\d{2}))",
    re.MULTILINE,
)


@register_parser(game_name, r"https://fermiquestions.org/#")
def fermi_estimate_parser(message: discord.Message):

    text = message.content

    data = pattern.search(text)

    if data is None:
        return
    result = data.groupdict()

    score = result["score_line"].count("⬆️") + result["score_line"].count("⬇️")

    date = datetime.datetime.strptime(result["date"], "%Y-%m-%d").date()

    game_number = utils.how_many_days_since_date(FERMI_ESTIMATE_ORIGIN_DATE, date)

    return float(score), date, int(game_number)
