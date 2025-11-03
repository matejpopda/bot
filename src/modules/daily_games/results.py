
import discord
import datetime
import discord
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy

from .. import database


import matplotlib.pyplot as plt
import io
import discord

import re

from .models import Scores




async def raw_game_data(game: str, user_id):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession

        result = []

        query = await session.execute(
            sqlalchemy.select(Scores)
            .where(Scores.user_id == user_id)
            .where(Scores.game == game)
            .order_by(Scores.date_of_game.asc())
        )
        for score in query.scalars():
            result.append(
                {
                    "score": score.score,
                    "date": score.date_of_game,
                    "gamenumber": score.game_number,
                }
            )

        return result






type User = discord.SlashCommandOptionType.user
async def generate_graph(
    game: str,
    player_1: User,
    player_2: User | None,
    player_3: User | None,
    player_4: User | None,
    dates_instead_of_numbers: bool,
):

    plt.figure(figsize=(6, 4))
    plt.title(f"{game} scores")
    plt.ylabel("Score")

    for index, player in enumerate([player_1, player_2, player_3, player_4]):

        if player is None:
            continue

        scores = await raw_game_data(game, player.id)

        if dates_instead_of_numbers:
            scores_x = [x["date"] for x in scores]
            plt.xlabel("Date")

        else:
            scores_x = [x["gamenumber"] for x in scores]
            plt.xlabel("Game number")

        scores_y = [x["score"] for x in scores]

        plt.plot(scores_x, scores_y, marker="o", label=f"{player.name}")

    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    plt.close()
    file = discord.File(buf, filename="score-history.png")
    return file
