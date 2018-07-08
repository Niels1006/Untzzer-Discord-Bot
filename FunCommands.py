import json

import discord
import random

import time

try:
    from src import UsefulMethods as um, Constants
except:
    import UsefulMethods as um, Constants




async def fight(bot, ctx, member):
    author = ctx.message.author
    channel = ctx.message.channel
    embed_title = "{0} [Level {2}] vs {1} [Level {3}]".format(author.name, member.name, get_level(author.id),
                                                              get_level(member.id))

    author_leben = 100
    member_leben = 100

    def update_leben(author_leben, member_leben):
        # global embed
        return discord.Embed(colour=Constants.EmbedColour).set_author(name=embed_title).add_field(
            name="{}'s HP".format(author.name),
            value=author_leben).add_field(
            name="{0}'s HP".format(member.name), value=member_leben)

    message = None
    while not author_leben <= 0 and not member_leben <= 0:
        author_schaden = random.choice(range(20))
        member_schaden = random.choice(range(20))

        author_leben -= member_schaden
        member_leben -= author_schaden
        if message is None:
            message = await bot.send_message(channel, embed=update_leben(author_leben, member_leben))
        else:
            message = await bot.edit_message(message, embed=update_leben(author_leben, member_leben))

        time.sleep(1)

    if author_leben <= 0:
        await bot.edit_message(message, embed=update_leben(author_leben, member_leben).add_field(
            name="{0} has won!".format(member.name), value="+10 Skill Rating ({} in total).".format(get_xp(member.id) + 10), inline=False))
        add_Skill_Rating(member.id, 10)

    else:
        await bot.edit_message(message, embed=update_leben(author_leben, member_leben).add_field(
            name="{0} has won!".format(author.name), value="+10 Skill Rating ({} in total).".format(get_xp(author.id) + 10), inline=False))
        add_Skill_Rating(author.id, 10)


def add_Skill_Rating(id, val):
    with open("data/userfights.json", "r") as f:
        data = json.load(f)
    try:
        data[str(id)] += val
    except:
        data[str(id)] = val

    with open("data/userfights.json", "w") as f:
        json.dump(data, f)


def get_level(id):
    with open("data/userfights.json", "r") as f:
        data = json.load(f)
    try:
        return int(data[id] / 20)
    except:
        return 1

def get_xp(id):
    with open("data/userfights.json", "r") as f:
        data = json.load(f)
    try:
        return data[id]
    except:
        return 0