import discord
from discord.ext import commands
import logging

console_logger = logging.getLogger("console")


class Debug(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        console_logger.info(f"We have logged in as {self.bot.user}")
        console_logger.info(f"Following cogs are active {[x for x in self.bot.cogs.keys()]}")
