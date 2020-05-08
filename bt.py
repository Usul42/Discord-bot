# bot.py
import os

import praw
import discord
from dotenv import load_dotenv

from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get

load_dotenv()

REDDIT_ID = os.getenv("REDDIT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ROOT = os.path.abspath(os.getcwd())
IMAGES = os.listdir(f"{ROOT}/images")
REDDIT = praw.Reddit(client_id=REDDIT_ID,
                     client_secret=REDDIT_SECRET,
                     user_agent="bot v0.1.0 by /u/borax")

bot = commands.Bot(command_prefix='!')

print("Reddit Read-Only connected", REDDIT.read_only)


@bot.command(
    name="reddit",
    description="A simple reddit parser",
    pass_context=True
)
async def reddit_function(ctx, *args):
    options = list(filter(lambda x: x.startswith("--"), args))
    values = list(filter(lambda x: not x.startswith("--"), args))
    if len(values) == 2:
        sub, nb = values
    else:
        sub = values[0]
        nb = 5
    nb = int(nb)
    if nb > 5:
        nb = 5
    for e in REDDIT.subreddit(sub).random_rising():
        try:
            if nb == 0:
                break
            embed = discord.Embed(
                author=e.author.name,
                title=e.title[0:256],
                url=e.shortlink,
            )
            if any([e.url.find(ext) >= 0 for ext in (".png", ".jpg", ".gif")]):
                embed.set_image(url=e.url)
            elif "--images" in options:
                continue
            await ctx.message.channel.send(embed=embed)
            nb -= 1
        except Exception as e:
            print("Error: ", e)


@bot.command(
    name="photo",
    description="Pour afficher les images entre potes :3",
    pass_context=True
)
async def photo_function(ctx, arg):
    if arg == "list":
        images_list = "\n".join(IMAGES)
        message = f"""
        Voilà la liste des images disponibles :) :

        {images_list}
        """
        await ctx.send(message)
    else:
        for image in IMAGES:
            if image.split(".")[0] == arg:
                file_name, path = [image, f"{ROOT}/images"]
                file = discord.File(f"{path}/{file_name}",
                                    filename=file_name)
                embed = discord.Embed()
                embed.set_image(url="attachment://"+file_name)
                await ctx.send(file=file, embed=embed)


@bot.command(
    name="joinme",
    description="Make the bot join your voice channel",
    pass_context=True
)
async def joinme(ctx):
    user = ctx.message.author
    voice_channel = user.voice.channel
    print("Join received", user, voice_channel)
    if voice_channel:
        print(f"joining {voice_channel}...")
        voice = get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(voice_channel)
        else:
            await voice_channel.connect()


@bot.command(
    name="disconnect",
    description="Make the bot leave your voice channel",
    pass_context=True
)
async def disconnect(ctx):
    user = ctx.message.author
    user_channel = user.voice.channel
    print("Disconnect received: ", user, user_channel)
    for voice_channel in bot.voice_clients:
        if voice_channel.channel == user_channel:
            print("disconnect...")
            await voice_channel.disconnect()


# @bot.event
# async def on_voice_state_update(member, prevstate, nextstate):
#     if (not prevstate.channel and nextstate.channel):
#         print(member, "have joined")
#         for voice_channel in bot.voice_clients:
#             source = FFmpegPCMAudio("file_example_MP3_700KB.mp3")
#             # voice = await voice_channel.connect()
#             await (source)


@bot.event
async def on_ready():
    print(
        f'Bot is connected:\n'
    )

bot.run(DISCORD_TOKEN)
