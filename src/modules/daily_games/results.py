import discord
import datetime
import discord
import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
import sqlalchemy.orm

from .. import database


import matplotlib.pyplot as plt
import seaborn as sns
import io
import discord

import re

from .models import Scores
from . import daily_games

import pandas as pd


async def raw_game_user_data(game: str, user_id):
    async with database.AsyncSessionLocal.begin() as session:
        session: AsyncSession
        result = []

        subq = (
            sqlalchemy.select(
                Scores.game_number,
                sqlalchemy.func.max(Scores.timestamp).label("latest_ts")
            )
            .where(Scores.user_id == user_id, Scores.game == game)
            .group_by(Scores.game_number)
            .subquery()
        )

        latest_scores = sqlalchemy.orm.aliased(Scores)

        query = await session.execute(
            sqlalchemy.select(latest_scores)
            .join(
                subq,
                (latest_scores.game_number == subq.c.game_number)
                & (latest_scores.timestamp == subq.c.latest_ts)
            )
            .where(latest_scores.user_id == user_id)
            .where(latest_scores.game == game)
            .order_by(latest_scores.date_of_game.asc())
        )
        for score in query.scalars():
            result.append(
                {
                    "score": score.score,
                    "date": score.date_of_game,
                    "gamenumber": score.game_number,
                    "user_id": score.user_id,
                }
            )
        return result


async def game_user_dataframe(game: str, user: discord.User):
    scores = await raw_game_user_data(game, user.id)
    data = pd.DataFrame(scores)
    data = data.rename(
        columns={
            "score": "Score",
            "user_id": "User",
            "date": "Date",
            "gamenumber": "Game Number",
        }
    )
    data = data.replace(user.id, user.name)
    return data


user_graph_types = [
    "Histogram",
    "Kernel Density Estimate",
    "Empirical Cumulative Distribution Function",
    "Scatter plot",
    "Line plot",
    "Linear regression",
]


async def generate_user_graph(
    game: str, user: discord.User, graph_type: str, dates_instead_of_numbers: bool
):
    data = await game_user_dataframe(game, user)

    if dates_instead_of_numbers:
        date_or_number = "Date"
    else:
        date_or_number = "Game Number"

    match graph_type:
        case "Histogram":
            g = sns.displot(data, x="Score", kind="hist", discrete=True, aspect=1.5)
        case "Kernel Density Estimate":
            g = sns.displot(data, x="Score", kind="kde", aspect=1.5)
        case "Empirical Cumulative Distribution Function":
            g = sns.displot(data, x="Score", kind="ecdf", aspect=1.5)
        case "Scatter plot":
            g = sns.relplot(
                data, y="Score", x=date_or_number, kind="scatter", aspect=1.5
            )
        case "Line plot":
            g = sns.relplot(data, y="Score", x=date_or_number, kind="line", aspect=1.5, markers="o", style="User", legend=None)
        case "Linear regression":
            g = sns.lmplot(data, y="Score", x=date_or_number, aspect=1.5)
        case _:
            raise ValueError("Unknown graph type")


    game_info = daily_games.get_game_info(game)
    g.ax.set(ylabel=game_info.score_name, title=f"{graph_type} graph of {game} scores for {user.name}")
    

    buf = io.BytesIO()
    g.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    file = discord.File(buf, filename="user_graph.png")
    return file


type User = discord.SlashCommandOptionType.user


async def generate_multiuser_graph(
    game: str,
    player_1: User,
    player_2: User | None,
    player_3: User | None,
    player_4: User | None,
    dates_instead_of_numbers: bool = False,
    scatter_instead_of_line: bool = False,
):

    data = []
    players = set(
        [x for x in (player_1, player_2, player_3, player_4) if x is not None]
    )

    for index, player in enumerate(players.copy()):

        if player is None:
            continue

        player_data = await game_user_dataframe(game, player)

        if len(player_data.index) == 0:
            players.remove(player)
            continue

        data.append(player_data)

    if len(data) == 0:
        raise ValueError("Trying to generate graph from no data")

    data = pd.concat(data, ignore_index=True)

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

    g = sns.relplot(
        data,
        y="Score",
        x=x,
        style="User",
        hue="User",
        kind=kind,
        facet_kws={"legend_out": False},
        aspect=1.5,
        markers=markers,
        dashes=False,
    )

    game_info = daily_games.get_game_info(game)
    g.ax.set(ylabel=game_info.score_name, title=f"Graph of {game} scores")

    buf = io.BytesIO()
    g.savefig(buf, format="png", dpi=200)
    buf.seek(0)
    file = discord.File(buf, filename="score-history.png")
    return file



