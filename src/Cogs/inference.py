import discord
from discord.ext import commands
import logging

from ..modules import inference
from ..modules import response_utils


console_logger = logging.getLogger("console")

song_logger = logging.getLogger("songs")


class Inference(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    llm_command_group = discord.SlashCommandGroup(
        "inference", "Using LLM to do some stuff"
    )

    @commands.Cog.listener()
    async def on_ready(self):
        pass 


    @llm_command_group.command(description="Talk to the bot.")
    @discord.option("mood", type=inference.Moods, default=inference.Moods.cat, description="Answering mood")
    @discord.option("ephemeral", type=bool, default=False, description="Should the output be hidden from others")
    async def anything_else(self, ctx: discord.ApplicationContext, mood,  ephemeral=True):
        response = ctx.interaction.response

        chanel: discord.abc.MessageableChannel = ctx.channel
        if chanel is None:
            await response_utils.send_error_response(ctx, "Cant access channel.")

        messages = list(reversed(await chanel.history(limit=50).flatten()))

        await response.defer(ephemeral=ephemeral)

        if self.bot.user is None:
            bots_username = "Unknown"
            logging.warning("For some reason the bot isnt logged in?")
        else:
            bots_username=self.bot.user.name

        try: 
            answer = await inference.add_to_chat(messages, mood, bots_username=bots_username)

            await response_utils.webhook_followup(ctx.followup, answer)
        except discord.errors.ApplicationCommandInvokeError as e:
            logging.error(e)
            await response_utils.send_error_webhook(ctx.followup, text="Failed to generate. Try again.")


    @llm_command_group.command(description="Talk to the bot.")
    @discord.option("text", type=str, required=True, description="What you want to tell the bot")
    @discord.option("mood", type=inference.Moods, default=inference.Moods.cat, description="Answer mood")
    @discord.option("ephemeral", type=bool, default=False, description="Should the output be hidden from others")
    async def converse(self, ctx: discord.ApplicationContext, text, mood,  ephemeral=True):
        response = ctx.interaction.response

        await response.defer(ephemeral=ephemeral)

        answer = await inference.single_question(text, mood)

        await response_utils.webhook_followup(ctx.followup, answer)
        
    @commands.command(name="converse")
    async def converse_text(self, ctx:commands.Context, *, text):
        msg = await ctx.reply("Thinking...")
        answer = await inference.single_question(text, inference.Moods.cat)
        await msg.edit(content=answer)


    @commands.message_command(description="Transcribes audio from the attachments of a message.")
    async def transcribe(self, ctx: discord.ApplicationContext, message: discord.Message) :
        response = ctx.interaction.response

        embed_urls: list[discord.EmbedMedia] = []
        attachments: list[discord.Attachment] = []
        for i in message.embeds:
            # if "audio" in i.type or "video" in i.type:
            if i.video is not None: 
                embed_urls.append(i.video)



        for i in message.attachments:
            attachments.append(i)


        if len(embed_urls) + len(attachments) == 0:
            await response_utils.send_error_response(ctx, f"No attachments.")
            return

        response_str = ""
        attachment_number = 1
        await response.defer(ephemeral=False)

        for attachment in attachments:
            if attachment.content_type is None:
                continue
            if "audio" in attachment.content_type:
                res = await attachment.read()
                response_str += f" Audio {attachment_number}: {str(await inference.transcribe_audio(res))} \n"
            if "video" in attachment.content_type:
                res = await attachment.read()
                response_str += f" Video {attachment_number}: {str(await inference.transcribe_video(res))} \n"
            attachment_number += 1

        for embed in embed_urls:
            res = await inference.download_video_from_embed(embed)
            if res is None:
                continue
            response_str += f" Embed {attachment_number}: {str(await inference.transcribe_video(res))} \n"
            attachment_number += 1

        if response_str == "":
            await response_utils.send_error_webhook(ctx.followup, "Couldn't parse the videos. Usually posting an embed proxy helps.")
            return

    

        await response_utils.send_success_webhook(ctx.followup, response_str, title="Audio Transcription")

        

    @commands.message_command(description="Describes message and its attachments.")
    async def describe(self, ctx: discord.ApplicationContext, message: discord.Message) :
        response = ctx.interaction.response

        await response.defer(ephemeral=False)
        response_str = await inference.describe_media(message)

        if response_str == "":
            await response_utils.send_error_webhook(ctx.followup, "Read message was empty. Not sure how you managed that.")
            return

    

        await response_utils.send_success_webhook(ctx.followup, response_str, title="Description")
