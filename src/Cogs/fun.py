import discord
from discord.ext import commands

import logging

import dyce
import numpy as np
import d20
import seaborn as sns
import matplotlib.pyplot as plt
import io
from ..modules import response_utils
import requests
import random




class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    fun = discord.SlashCommandGroup("fun", "Random collection of fun tools")

    @fun.command(description="Get a random InspiroBot image")
    async def inspiring_image(self, ctx: discord.ApplicationContext):
        image = requests.get("https://inspirobot.me/api?generate=true")
        image.raise_for_status()
        image_url = image.text

        embed = response_utils.default_text_embed(title="Get inspired",image=image_url)
        await ctx.respond(embed=embed)

    @fun.command(description="Get a random InspiroBot quote")
    async def inspiring_quote(self, ctx: discord.ApplicationContext):
        url = "https://inspirobot.me/api?generateFlow=1"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        quotes = [entry["text"] for entry in data["data"] if entry["type"] == "quote"]
        quote = random.choice(quotes)

        embed = response_utils.default_text_embed(title="Reflect",text=quote)
        await ctx.respond(embed=embed)


    @fun.command(description="Get a random dad joke from https://icanhazdadjoke.com/")
    async def dad_joke(self, ctx: discord.ApplicationContext):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "text/plain"}
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        quote = response.text
        embed = response_utils.default_text_embed(title="Dad joke",text=quote)
        await ctx.respond(embed=embed)


    @fun.command(description="Get a random advice from https://adviceslip.com/")
    async def advice(self, ctx: discord.ApplicationContext):
        url = "https://api.adviceslip.com/advice"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        advice = data["slip"]["advice"]
        embed = response_utils.default_text_embed(title="Random advice",text=advice)
        await ctx.respond(embed=embed)
