import logging
import discord 
import dotenv
import src.Cogs.gamestatistics as gamestatistics
import src.Cogs.debug as debug
import src.Cogs.ttrpgtools as ttrpgtools
 

if __name__ == "__main__":
    bot = discord.Bot()
    config = dotenv.dotenv_values()
    

    bot.add_cog(debug.Debug(bot))
    bot.add_cog(gamestatistics.GameStatistics(bot))
    bot.add_cog(ttrpgtools.TttrpgTools(bot))




    bot.run(config["TOKEN"])