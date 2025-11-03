import discord
from discord.ext import commands
import logging


class Debug(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f"We have logged in as {self.bot.user}")
