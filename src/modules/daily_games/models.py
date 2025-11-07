from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from collections.abc import Callable

from .. import database

import datetime


class RegisteredChannels(database.Base):
    __tablename__ = "registered_channels"
    channel_id: Mapped[int] = mapped_column(primary_key=True)
    who_registered_user_id: Mapped[int]
    timestamp_of_registration: Mapped[datetime.datetime]
    guild_id: Mapped[int]


class Scores(database.Base):
    __tablename__ = "scores"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[float]
    user_id: Mapped[int]
    channel_id: Mapped[int]
    guild_id: Mapped[int]
    game: Mapped[str] = mapped_column(primary_key=True)
    date_of_game: Mapped[datetime.date]
    game_number: Mapped[int]
    timestamp: Mapped[datetime.datetime]
