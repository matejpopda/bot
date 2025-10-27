import logging
import discord 
import dotenv
import src.Cogs.gamestatistics as gamestatistics
import src.Cogs.debug as debug
import src.Cogs.ttrpgtools as ttrpgtools
 

default_command_integration_types=set([discord.IntegrationType.guild_install, 
                                       discord.IntegrationType.user_install])

if __name__ == "__main__":

    bot = discord.Bot(default_command_integration_types=default_command_integration_types)
    config = dotenv.dotenv_values()
    

    bot.add_cog(debug.Debug(bot))
    bot.add_cog(gamestatistics.GameStatistics(bot))
    bot.add_cog(ttrpgtools.TttrpgTools(bot))




    bot.run(config["TOKEN"])