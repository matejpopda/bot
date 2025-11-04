
import discord
import datetime
import discord
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy

from .. import database


import matplotlib.pyplot as plt
import seaborn as sns
import io
import discord

import re

from .models import Scores


import pandas as pd

async def raw_game_user_data(game: str, user_id):
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
                    "user_id": score.user_id
                }
            )

        return result






type User = discord.SlashCommandOptionType.user
async def generate_multiuser_graph(
    game: str,
    player_1: User,
    player_2: User | None,
    player_3: User | None,
    player_4: User | None,
    dates_instead_of_numbers: bool= False,
    scatter_instead_of_line:bool = False,
):

    all_scores = []
    players = set([x for x in (player_1, player_2, player_3, player_4) if x is not None])

    for index, player in enumerate(players.copy()):

        if player is None:
            continue

        scores = await raw_game_user_data(game, player.id)

        if len(scores) == 0:
            players.remove(player)
            continue

        all_scores.extend(scores)

    if len(all_scores) == 0:
        raise ValueError("Trying to generate graph from no data")

    data = pd.DataFrame(all_scores)

    for player in players:
        data = data.replace(player.id, player.name)

    data = data.rename(columns={"score":"Score", "user_id":"User", "date":"Date", "gamenumber":"Game Number"})


    if dates_instead_of_numbers:
        x = "Date"
    else:
        x = "Game Number"

    if scatter_instead_of_line:
        kind = "scatter"
        markers = True
    else:
        kind = "line"
        markers = ["o" for x in players]

    g = sns.relplot(data, y="Score", x=x, style="User", hue="User", kind=kind, facet_kws={"legend_out":False}, aspect=1.5, markers=markers, dashes=False)

        
    g.figure.subplots_adjust(top=.92)
    g.figure.suptitle(f'Game scores for {game}')

    buf = io.BytesIO()
    g.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    file = discord.File(buf, filename="score-history.png")
    return file
