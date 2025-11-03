import logging
import asyncio

import discord
import discord.ext.commands as commands
import dotenv
import src.Cogs.gamestatistics as gamestatistics
import src.Cogs.debug as debug
import src.Cogs.ttrpgtools as ttrpgtools
import src.Cogs.fun as fun

from io import BytesIO

from src.modules.database import engine, Base
from src.modules import formatting

import src.modules.logging

integration_types = set(
    [discord.IntegrationType.guild_install, discord.IntegrationType.user_install]
)

intents = discord.Intents.default()
intents.message_content = True


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_db()

    config = dotenv.dotenv_values()
    bot = commands.Bot(
        default_command_integration_types=integration_types, intents=intents
    )

    bot.add_cog(debug.Debug(bot))
    bot.add_cog(gamestatistics.GameStatistics(bot))
    bot.add_cog(ttrpgtools.TttrpgTools(bot))
    bot.add_cog(fun.Fun(bot))

    await bot.start(config["TOKEN"])


if __name__ == "__main__":
    src.modules.logging.setup_all_logging()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutting down...")
