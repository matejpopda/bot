import logging

import src.modules.logging
src.modules.logging.setup_all_logging()

import asyncio

import discord
import discord.ext.commands as commands
import dotenv


import src.Cogs.daily_games as daily_games
import src.Cogs.debug as debug
import src.Cogs.ttrpgtools as ttrpgtools
import src.Cogs.fun as fun


import src.modules.database 
import src.modules.response_utils  

integration_types = set(
    [discord.IntegrationType.guild_install, discord.IntegrationType.user_install]
)

intents = discord.Intents.default()
intents.message_content = True

console_logger = logging.getLogger("console")


async def main():
    
    src.modules.response_utils.set_default_graph_formatting()

    config = dotenv.dotenv_values("config_files/.env")
    bot = commands.Bot(
        default_command_integration_types=integration_types, 
        intents=intents
    )

    await src.modules.database.init_db()

    bot.add_cog(debug.Debug(bot))
    bot.add_cog(daily_games.GameStatistics(bot))
    bot.add_cog(ttrpgtools.TttrpgTools(bot))
    bot.add_cog(fun.Fun(bot))

    assert isinstance(config["TOKEN"], str)
    await bot.start(config["TOKEN"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console_logger.info("Bot shutting down...")
