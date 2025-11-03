import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

FERMI_ESTIMATE_ORIGIN_DATE = datetime.date(day=23, month=7, year=2025)




@register_parser("Fermi Estimate", r"https://fermiquestions.org/#")
def fermi_estimate_parser(message: discord.Message):

    text = message.content
    pattern = re.compile(
        r"^(?:.*\n)*?"
        r"(?P<score_line>(?:[⬆️⬇️]+)?✅?)\s*\n"
        r"(?P<url>https?://fermiquestions\.org/#/(?P<date>\d{4}-\d{2}-\d{2}))",
        re.MULTILINE,
    )

    data = pattern.search(text)

    if data is None:
        return
    result = data.groupdict()

    score = result["score_line"].count("⬆️") + result["score_line"].count("⬇️")

    date = datetime.datetime.strptime(result["date"], "%Y-%m-%d").date()

    game_number = utils.how_many_days_since_date(FERMI_ESTIMATE_ORIGIN_DATE, date)

    return float(score), date, int(game_number)