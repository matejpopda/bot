import logging
import asyncio

import discord
import discord.ext.commands as commands
import dotenv
import src.Cogs.gamestatistics as gamestatistics
import src.Cogs.debug as debug
import src.Cogs.ttrpgtools as ttrpgtools
import src.Cogs.fun as fun


import src.modules.database 

import src.modules.logging
import  src.modules.formatting  

integration_types = set(
    [discord.IntegrationType.guild_install, discord.IntegrationType.user_install]
)

intents = discord.Intents.default()
intents.message_content = True




async def main():
    src.modules.logging.setup_all_logging()
    src.modules.formatting.set_default_graph_formatting()

    config = dotenv.dotenv_values()
    bot = commands.Bot(
        default_command_integration_types=integration_types, 
        intents=intents
    )

    await src.modules.database.init_db()

    bot.add_cog(debug.Debug(bot))
    bot.add_cog(gamestatistics.GameStatistics(bot))
    bot.add_cog(ttrpgtools.TttrpgTools(bot))
    bot.add_cog(fun.Fun(bot))

    await bot.start(config["TOKEN"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutting down...")
