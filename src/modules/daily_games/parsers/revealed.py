import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser

REVEALED_ORIGIN_DATE = datetime.date(day=6, month=10, year=2025)




@register_parser("Revealed", r"REVEALED: ")
def revealed_parser(message: discord.Message):
    text = message.content

    pattern = re.compile(
        r"(?m)^REVEALED:\s*(?P<date_str>[A-Za-z]+ \d{1,2}, \d{4})\s*.*?"
        r"(?:I solved it in\s*(?P<reveals_raw>[\d️⃣]+)\s*Reveals\s*&\s*(?P<hints_raw>[\d️⃣]+)\s*Hints|"
        r"I couldn’t solve it.*?)",
        re.DOTALL,
    )

    data = pattern.search(text)
    if data is None:
        return
    result = data.groupdict()

    def emoji_to_int(s):
        if not s:
            return None
        digits = re.findall(r"\d", s)
        return int("".join(digits)) if digits else 0

    reveals = emoji_to_int(result["reveals_raw"])
    hints = emoji_to_int(result["hints_raw"])
    if reveals is None:
        score = 7 + 4 + 1  # max reveal + max hints + 1
    else:
        score = reveals + hints

    date = datetime.datetime.strptime(result["date_str"], "%b %d, %Y").date()

    game_number = utils.how_many_days_since_date(REVEALED_ORIGIN_DATE, date)

    return float(score), date, int(game_number)