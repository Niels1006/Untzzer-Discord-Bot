import json, discord

import time
from datetime import date
from _thread import start_new_thread

import asyncio

try:
    from main import UsefulMethods, Constants
except:
    import UsefulMethods, Constants

points = {"!mute": 10,
          "!warn": 15,
          "!ban": 2,
          "!kick": 3,
          "message": 1}

msgs = {"!mute": 10,
        "!warn": 15,
        "message": 1}

# async def get_invite(bot, author, channel):
#     def openJ():
#         with open("data/userinfos.json", "r") as f:
#             return json.load(f)
#
#     def saveJ(data):
#         with open("data/userinfos.json", "w") as f:
#             json.dump(data, f)
#
#     data = openJ()
#     if not author.id in data["invites"]:
#         inv = await bot.create_invite(channel)
#         data["invites"][author.id] = {"username": author.name,
#                                       "invite_id": inv.id}
#         saveJ(data)

cache_msg = {}


def event_message(message):
    global cache_msg
    try:
        cache_msg[message.author.id]
    except:
        cache_msg[message.author.id] = "09834528548543789576jiofdsjnksfkj"

    if cache_msg[message.author.id].lower() == message.content:
        addPoints(message.author, "message", -2)

    else:
        for msg in msgs:
            if message.content.lower().startswith(msg):
                addPoints(message.author, msg, 1)
        addPoints(message.author, "message", 1)

    cache_msg[message.author.id] = message.content


def stats_embed(member):
    if not checkJSON(member):
        return UsefulMethods.buildBaseEmbed(member, "Activity System", "No recorded data")

    return [UsefulMethods.buildBaseEmbed(member, "Activity Stats for {}".format(member), stats(member.id)[0]),
            stats(member.id)[1]]


def stats(memberid, user = False):
    data = openJSON()[memberid]
    out = ""
    total = 0
    for befehl in sorted(points):
        out += "**{:4d}** {:10s} **{:5d}** Points{}".format(
            data[befehl], befehl.replace("!", "").title() + "s:", data[befehl] * points[befehl],
            "\n")
        total += data[befehl] * points[befehl]

    if user is True:
        befehl = "message"
        out = "**{:4d}** {:10s} **{:5d}** Points{}".format(
            data[befehl], befehl.replace("!", "").title() + "s:", data[befehl] * points[befehl],
            "\n")

    return [out, total, memberid]


def leaderboard_mods(author, server=None):
    if server is None:
        server = author.server
    data = openJSON()

    all_stats = []
    for memberid in list(data):
        try:
            user = discord.utils.find(lambda u: u.id == memberid, server.members)

            for role in user.roles:
                if role.name.lower() == "moderators":
                    all_stats.append(stats(memberid))
        except:
            del data[memberid]
            print("deleted an user")
            saveJSON(data)

    i = 1
    while i < len(all_stats):
        if all_stats[i][1] > all_stats[i - 1][1]:
            help = all_stats[i]
            all_stats[i] = all_stats[i - 1]
            all_stats[i - 1] = help
            if not i == 1:
                i -= 1
        else:
            i += 1

    embed = UsefulMethods.buildBaseEmbed(author, "Activity Leaderboards")

    place = 1
    for x in all_stats:
        embed.add_field(name="{0}. Place: `{1}` (Total Points: {2})".format(place,
                                                                            discord.utils.find(lambda m: m.id == x[2],
                                                                                               server.members),
                                                                            x[1]), value=x[0],
                        inline=False)
        place += 1

    return embed


def leaderboard_users(author, server=None):
    if server is None:
        server = author.server
        print("None")
    data = openJSON()

    all_stats = []
    for memberid in list(data):
        user = discord.utils.find(lambda u: u.id == memberid, server.members)
        moderator_role = discord.utils.find(lambda r: r.name.lower() == "moderators", server.roles)
        try:
            if user.top_role < moderator_role:
                all_stats.append(stats(memberid, True))
        except:
            del data[memberid]
            print("deleted an user")
            saveJSON(data)

    i = 1
    while i < len(all_stats):
        if all_stats[i][1] > all_stats[i - 1][1]:
            help = all_stats[i]
            all_stats[i] = all_stats[i - 1]
            all_stats[i - 1] = help
            if not i == 1:
                i -= 1
        else:
            i += 1

    embed = UsefulMethods.buildBaseEmbed(author, "Activity Leaderboards")

    place = 1
    for x in all_stats[:10]:
        embed.add_field(name="{0}. Place: `{1}` (Total Points: {2})".format(place,
                                                                            discord.utils.find(lambda m: m.id == x[2],
                                                                                               server.members),
                                                                            x[1]), value=x[0],
                        inline=False)
        place += 1

    return embed


async def checkForReset(bot):
    heute = date.today()

    wt = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")[heute.weekday()]

    with open("data/settings.json", "r") as f:
        data = json.load(f)

    if time.time() - data["vanguard_last_reset"] > 20000 and wt == "Samstag":
        data["vanguard_last_reset"] = time.time()
    else:
        return

    await bot.send_message(discord.utils.find(lambda c: c.id == Constants.vanguardChannelID,
                                              discord.utils.find(lambda s: s.id == Constants.vanguardServerID,
                                                                 bot.servers).channels),
                           embed=leaderboard_mods(bot.user,
                                                  discord.utils.find(lambda s: s.id == Constants.vanguardServerID,
                                                                     bot.servers)))

    await bot.send_message(discord.utils.find(lambda c: c.id == Constants.vanguardUserChannelID,
                                              discord.utils.find(lambda s: s.id == Constants.vanguardServerID,
                                                                 bot.servers).channels),
                           embed=  leaderboard_users(bot.user,
                                                  discord.utils.find(lambda s: s.id == Constants.vanguardServerID,
                                                                     bot.servers)))
    with open("data/settings.json", "w") as f:
        json.dump(data, f)

    data = openJSON()
    data = {}
    saveJSON(data)


def addPoints(member, befehl, points):
    data = openJSON()
    try:
        data[member.id][befehl] += points
    except:
        data[member.id] = {"!mute": 0,
                           "!warn": 0,
                           "!ban": 0,
                           "!kick": 0,
                           "message": 0}
        data[member.id][befehl] += points
    saveJSON(data)


def checkJSON(member):
    try:
        openJSON()[member.id]
        return True
    except:
        return False


def openJSONCheck():
    return ""


def openJSON():
    with open("data/vanguard.json", "r") as f:
        return json.load(f)


def saveJSON(data):
    with open("data/vanguard.json", "w") as f:
        json.dump(data, f)
