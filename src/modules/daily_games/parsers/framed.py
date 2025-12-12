import datetime
import discord
import re
from .. import utils
from ..daily_games import register_parser
from ..daily_games import add_game_info

FRAMED_FIRST_GAME_DATE = datetime.date(year=2022, month=3, day=11)
game_name = "Framed"


game_info = utils.GameInfo( game_name=game_name
                            ,fail_score=7
                            ,lower_score_is_better=True
                            ,score_name="Number of guesses"
                            ,url="https://framed.wtf/"
                            ,description="Guess the movie based on screenshots."
                            )

add_game_info(game_name, game_info)



pattern = re.compile(
    r'Framed\s+#(?P<game_number>\d+)\s*\n'
    r'🎥(?P<guesses>(?:\s*[⬛🟥🟩])+)',
    re.MULTILINE
)

@register_parser(game_name, r"^Framed")
def framed_parser(message: discord.Message) -> tuple[float, datetime.date, int] | None:

    text = message.content

    score = None

    data = pattern.search(text)
    if data is None:
        return

    result = data.groupdict()

    for m in pattern.finditer(text):
        guesses = m.group("guesses").strip().split()
        score = guesses.index("🟩") + 1 if "🟩" in guesses else 7

    if score is None:
        return
    game_number = int(result["game_number"])

    date = utils.date_after_days_passed(FRAMED_FIRST_GAME_DATE, game_number)



    return float(score), date, game_number
