# bot.py
import os

import praw
import discord
from dotenv import load_dotenv

load_dotenv()

REDDIT_ID = os.getenv("REDDIT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ROOT = os.path.abspath(os.getcwd())
IMAGES = os.listdir(f"{ROOT}/images")
REDDIT = praw.Reddit(client_id=REDDIT_ID,
                     client_secret=REDDIT_SECRET,
                     user_agent="bot v0.1.0 by /u/borax")
print("REDDIT READ ONLY", REDDIT.read_only)


async def commands_function(message):
    msg = "\n".join([f"{c}" for c in COMMANDS.keys()])
    await message.channel.send(msg)


async def reddit_function(message):
    commands = message.content.lower().split(" ")[1:]
    opt_list = list(filter(lambda x: x.startswith("--"), commands))
    args = list(filter(lambda x: not x.startswith("--"), commands))
    if len(args) == 2:
        sub, nb = args
    else:
        sub = args[0]
        nb = 10
    nb = int(nb)
    print(sub, nb, opt_list, args)
    try:
        for e in REDDIT.subreddit(sub).hot(limit=None):
            if nb == 0:
                break
            embed = discord.Embed(
                author=e.author.name,
                title=e.title[0:256],
                url=e.shortlink,
            )
            if any([e.url.find(ext) >= 0 for ext in (".png", ".jpg", ".gif")]):
                embed.set_image(url=e.url)
            elif "--images" in opt_list:
                continue
            await message.channel.send(embed=embed)
            nb -= 1
    except Exception as e:
        print("ERROR:", e)


async def image_function(message, image):
    file = discord.File(f"{image['path']}/{image['file']}",
                        filename=image["file"])
    embed = discord.Embed()
    embed.set_image(url="attachment://"+image["file"])
    await message.channel.send(file=file, embed=embed)


COMMANDS = {
    "!reddit": {"function": reddit_function,
                "type": "fct"},
    "!commands": {"function": commands_function,
                  "type": "fct"},
}

COMMANDS.update({
    f"!{image_file.split('.')[0]}": {
        "type": "image",
        "function": image_function,
        "file": image_file,
        "path": f"{ROOT}/images"
    } for image_file in IMAGES})

client = discord.Client()


@client.event
async def on_message(message):
    if not message.content.lower().startswith("!"):
        return
    cmd = COMMANDS.get(message.content.lower().split()[0])
    if cmd:
        if cmd["type"] == "fct":
            await cmd["function"](message)
        if cmd["type"] == "image":
            await cmd["function"](message, cmd)


@client.event
async def on_ready():
    print(
        f'{client.user} is connected:\n'
    )

client.run(DISCORD_TOKEN)
