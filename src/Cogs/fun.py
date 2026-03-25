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
from ..modules.fun import noun_verbed 

import PIL.Image as Image


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



    @fun.command(description="Create a noun verbed image")
    @discord.option("text_type", type=noun_verbed.TextTypes, default=noun_verbed.TextTypes.victory_achieved, description="Type of overlay")
    @discord.option("text", type=str, description="Text", required=False)
    @discord.option("image_url", type=str, description="Url of image to overlay onto, transparent bg otherwise", required=False)
    async def noun_verbed(self, ctx: discord.ApplicationContext, text:str, text_type:noun_verbed.TextTypes, image_url:str|None):


        if image_url is not None:
            response = requests.get(image_url)
            response.raise_for_status()
            image= Image.open(io.BytesIO(response.content))
        else: 
            image=None

        image = noun_verbed.noun_verbed(text, text_type=text_type, user_image=image) 

        with io.BytesIO() as image_binary:
                            image.save(image_binary, 'PNG')
                            image_binary.seek(0)
                            file = discord.File(image_binary, filename="nounverbed.png")

                            await ctx.respond(file=file)
