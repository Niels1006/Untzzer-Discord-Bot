import discord
import json, time
import asyncio

try:
    from main import UsefulMethods as um
except:
    import UsefulMethods as um

permittedroles = []


def get_server(bot, name):
    for s in bot.servers:
        if s.name == name:
            return s


def getMiddlemanChannel(server):
    for c in server.channels:
        if c.name == "middleman-cases":
            return c


def checkPermitted(author):
    if author.id == "213420388741283840":
        return True
    for r in author.roles:
        if r.name in ["Staff", "Overseer", "Owner", "Certified Middlemen"]:
            return True
    return False


def getMiddlemanRole(server, platform):
    platform= platform.title() if platform.lower() in ["xbox", "switch"] else platform.upper()
    for r in server.roles:
        if r.name == "{0} MM".format(platform):
            return r


def openMM():
    with open("data/middleman.json", "r") as f:
        return json.load(f)


def saveMM(data):
    with open("data/middleman.json", "w") as f:
        json.dump(data, f)


async def call(bot, ctx, trade_partner, platform, description):
    if not ctx.message.channel.name == "middleman-call":
        await bot.send_message(ctx.message.author, embed=um.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                                           "You have to go to #middleman-call to call a middleman."))
        await bot.delete_message(ctx.message)

        return

    data = openMM()
    server = ctx.message.server
    tradeid = len(data)

    for i in range(len(data)):
        i = str(i)
        if data[i]["callerid"] == ctx.message.author.id and data[i][
            "active"]:
            msg = await bot.send_message(ctx.message.channel,
                                         embed=um.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                                 "You are still in an open middleman call.").add_field(
                                             name="Trade {0}".format(i), value="\u200b  **Caller**: {0}\n"
                                                                               "  **Partner**: {1}\n"
                                                                               "  **Description**: {2}\n"
                                                                               "  **ID**: {3}".format(
                                                 ctx.message.server.get_member(
                                                     data[i][
                                                         "callerid"]).mention,
                                                 ctx.message.server.get_member(
                                                     data[i][
                                                         "partnerid"]).mention,

                                                 data[i]["description"], data[i]["id"])))
            await asyncio.sleep(15)
            for m in [msg, ctx.message]:
                await bot.delete_message(m)

            return
            # data.append("trade{}".format(len(data)))

    readperm = discord.PermissionOverwrite(read_messages=True)
    everyone = discord.PermissionOverwrite(read_messages=False)

    channel = await bot.create_channel(server, "trade{}".format(tradeid), (server.default_role, everyone),
                                       (ctx.message.author, readperm), (trade_partner, readperm),
                                       (ctx.message.server.get_member("213420388741283840"), readperm))

    data[str(tradeid)] = {
        "partnerid": trade_partner.id,
        "partnername": trade_partner.name,
        "callerid": ctx.message.author.id,
        "callername": ctx.message.author.name,
        "platform": platform,
        "description": description,
        "id": tradeid,
        "channelid": channel.id,
        "active": True,
        "middlemanname": None,
        "middlemanid": None,
        "confirmcaller": False,
        "confirmpartner": False,
        "creationtime": time.time(),
        "callmessageid": None
    }

    await bot.send_message(channel,
                           "Hey {0} and {1}, please confirm your trade `{2}` by typing !yes. You have 10 minutes until the trade gets deleted.".format(
                               ctx.message.author.mention, trade_partner.mention, description))
    await bot.delete_message(ctx.message)
    saveMM(data)
    await asyncio.sleep(600)

    print("open")
    data = openMM()

    if data[str(tradeid)]["confirmpartner"] == False or data[str(tradeid)][
        "confirmcaller"] == False:
        for u in [ctx.message.author, trade_partner]:
            await bot.send_message(u, "You were too slow, your trade `{0}` got deleted.".format(description))

        await bot.delete_channel(channel)

        del data[str(tradeid)]

        saveMM(data)
        print("deleted")


async def yes(bot, ctx):
    data = openMM()
    for i in range(len(data)):
        i = str(i)
        if data[i]["callerid"] == ctx.message.author.id and data[i]["confirmcaller"] == False:
            data[i]["confirmcaller"] = True
            saveMM(data)
            await bot.send_message(bot.get_channel(data[i]["channelid"]),
                                   embed=um.buildBaseEmbed(ctx.message.author, "Middleman Call",
                                                           "Succesfully confirmed the trade."))

            if data[i]["confirmcaller"] == True and data[i]["confirmpartner"] == True:
                await bot.send_message(bot.get_channel(data[i]["channelid"]),
                                       embed=um.buildBaseEmbed(ctx.message.author, "Middleman Call",
                                                               "Both accepted the trade. A middleman will be with you shortly."))
                await callMiddleMan(bot, ctx, i)
        elif data[i]["partnerid"] == ctx.message.author.id and data[i]["confirmpartner"] == False:
            data[i]["confirmpartner"] = True
            saveMM(data)
            await bot.send_message(bot.get_channel(data[i]["channelid"]),
                                   embed=um.buildBaseEmbed(ctx.message.author, "Middleman Call",
                                                           "Succesfully confirmed the trade."))
            if data[i]["confirmcaller"] == True and data[i]["confirmpartner"] == True:
                await bot.send_message(bot.get_channel(data[i]["channelid"]),
                                       embed=um.buildBaseEmbed(ctx.message.author, "Middleman Call",
                                                               "Both accepted the trade. A middleman will be with you shortly."))

                await callMiddleMan(bot, ctx, i)


async def callMiddleMan(bot, ctx, id):
    data = openMM()
    msg = await bot.send_message(getMiddlemanChannel(ctx.message.server),
                                 getMiddlemanRole(ctx.message.server, data[id]["platform"]).mention,
                                 embed=um.buildBaseEmbed(ctx.message.author, "Middleman Needed",
                                                         "{0} and {1} require assistance in `{3}`, ID: `{2}`, Platform `{4}`. Type `!confirm {2}` to accept the case.".format(
                                                             ctx.message.server.get_member(
                                                                 data[id]["callerid"]).mention,
                                                             ctx.message.server.get_member(
                                                                 data[id]["partnerid"]).mention,
                                                             id, data[id]["description"], data[id]["platform"])))
    data[id]["callmessageid"] = msg.id
    saveMM(data)


async def cancel(bot, ctx):
    data = openMM()

    for i in range(len(data)):
        i = str(i)
        if data[i]["callerid"] == ctx.message.author.id and data[i]["active"] and data[i]["middlemanid"] is None:
            await bot.delete_channel(ctx.message.server.get_channel(data[i]["channelid"]))
            msg = await bot.send_message(ctx.message.channel,
                                         embed=um.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                                 "Succesfully canceled middleman call {}.".format(
                                                                     i)))
            del data[i]
            saveMM(data)
            await asyncio.sleep(5)
            await bot.delete_message(msg)
            return

    await bot.send_message(ctx.message.channel, embed=um.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                                        "You don't have an open middleman call or a middleman accepted the call."))


async def confirm(bot, ctx, id):
    if not checkPermitted(ctx.message.author):
        return um.buildBaseEmbed(ctx.message.author, "Middleman System", "You aren't a certified middleman.")

    data = openMM()
    data[str(id)]["middlemanname"] = ctx.message.author.name
    data[str(id)]["middlemanid"] = ctx.message.author.id
    readperm = discord.PermissionOverwrite(read_messages=True)

    print(data[id]["callmessageid"])

    await bot.edit_channel_permissions(ctx.message.server.get_channel(data[id]["channelid"]),
                                       ctx.message.author, readperm)

    await bot.delete_message(await bot.get_message(ctx.message.channel, data[id]["callmessageid"]))
    await bot.delete_message(ctx.message)
    print("Save MM.json")

    msg = await bot.send_message(ctx.message.channel, embed=um.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                                              "You are a middleman in trade{0} now. Make sure to `!close {0}` the trade if the trade finished or `!delete {0}` if the trade failed.".format(
                                                                                  id)).add_field(name="Trade Members",
                                                                                                 value="Caller: {0}, Partner: {1}.".format(
                                                                                                     ctx.message.server.get_member(
                                                                                                         data[id][
                                                                                                             "callerid"]).mention,
                                                                                                     ctx.message.server.get_member(
                                                                                                         data[id][
                                                                                                             "partnerid"]).mention),
                                                                                                 inline=False).add_field(
        name="Trade Description", value=data[id]["description"], inline=False).add_field(name="Middleman",
                                                                                         value=ctx.message.server.get_member(
                                                                                             data[id][
                                                                                                 "middlemanid"]).mention,
                                                                                         inline=False))
    data[id]["callmessageid"] = msg.id
    saveMM(data)


async def close(bot, ctx, id):
    if not checkPermitted(ctx.message.author):
        return um.buildBaseEmbed(ctx.message.author, "Middleman System", "You aren't a certified middleman.")
    data = openMM()
    data[id]["active"] = False
    saveMM(data)

    for msg in [ctx.message.id, data[id]["callmessageid"]]:
        await bot.delete_message(await bot.get_message(ctx.message.channel, msg))

    await bot.delete_channel(ctx.message.server.get_channel(data[id]["channelid"]))

    await bot.send_message(um.getChannel(bot, "mm-logs"),
                           embed=um.buildBaseEmbed(ctx.message.author, "Middleman System".format(id),
                                                   "Trade {0} closed".format(id)).add_field(name="Trade Stats",
                                                                                            value="\u200b  **Caller**: {0}\n"
                                                                                                  "  **Partner**: {1}\n"
                                                                                                  "  **Middleman**: {2}\n"
                                                                                                  "  **Description**: {3}\n"
                                                                                                  "  **Platform**: {5}\n"
                                                                                                  "  **ID**: {4}".format(
                                                                                                ctx.message.server.get_member(
                                                                                                    data[id][
                                                                                                        "callerid"]).mention,
                                                                                                ctx.message.server.get_member(
                                                                                                    data[id][
                                                                                                        "partnerid"]).mention,
                                                                                                ctx.message.server.get_member(
                                                                                                    data[id][
                                                                                                        "middlemanid"]).mention,
                                                                                                data[id]["description"],
                                                                                                data[id]["id"], data[id]["platform"])))


async def gettrades(ctx, user):
    if not checkPermitted(ctx.message.author):
        return um.buildBaseEmbed(ctx.message.author, "Middleman Database", "You aren't a certified middleman.")
    data = openMM()
    tradeids = []
    for i in range(len(data)):
        i = str(i)
        if data[i]["middlemanid"] == user.id and not data[i]["active"]:
            tradeids.append(i)

    if len(tradeids) > 0:
        em = um.buildBaseEmbed(user, "Middleman Database", "{0} saved trades.".format(len(tradeids)))
        for i in tradeids:
            em.add_field(name="Trade {0}".format(i), value="\u200b  **Caller**: {0}\n"
                                                           "  **Partner**: {1}\n"
                                                           "  **Middleman**: {2}\n"
                                                           "  **Description**: {3}\n"
                                                           "  **ID**: {4}\n"
                                                           "  **Platform**: {5}".format(
                ctx.message.server.get_member(
                    data[i][
                        "callerid"]).mention,
                ctx.message.server.get_member(
                    data[i][
                        "partnerid"]).mention,
                ctx.message.server.get_member(
                    data[i][
                        "middlemanid"]).mention,
                data[i]["description"], data[i]["id"], data[i]["platform"]))
    else:
        em = um.buildBaseEmbed(user, "Middleman Database", "This Middleman has 0 saved trades.".format(len(tradeids)))
    return em


async def gettrade(ctx, id):
    if not checkPermitted(ctx.message.author):
        return um.buildBaseEmbed(ctx.message.author, "Middleman Database", "You aren't a certified middleman.")
    data = openMM()
    if id is not None:
        em = um.buildBaseEmbed(ctx.message.author, "Middleman Database", "{0} saved trades.".format(len(data)))
        em.add_field(name="Trade {0}".format(id), value="\u200b  **Caller**: {0}\n"
                                                        "  **Partner**: {1}\n"
                                                        "  **Middleman**: {2}\n"
                                                        "  **Description**: {3}\n"
                                                        "  **ID**: {4}\n"
                                                        "  **Platform**: {5}".format(
            ctx.message.server.get_member(
                data[id][
                    "callerid"]).mention,
            ctx.message.server.get_member(
                data[id][
                    "partnerid"]).mention,
            ctx.message.server.get_member(
                data[id][
                    "middlemanid"]).mention,
            data[id]["description"], data[id]["id"], data[id]["platform"]))
    else:
        em = um.buildBaseEmbed(ctx.message.author, "Middleman Database",
                               "{0} saved trades. (0-{1}).".format(len(data), len(data) - 1))
    return em


async def delete(ctx, id, bot=None):
    if not checkPermitted(ctx.message.author):
        return um.buildBaseEmbed(ctx.message.author, "Middleman Database", "You aren't a certified middleman.")
    data = openMM()
    if data[id]["active"]:
        await bot.delete_channel(ctx.message.server.get_channel(data[id]["channelid"]))
    del data[id]
    saveMM(data)
    return um.buildBaseEmbed(ctx.message.author, "Middleman Database", "Succesfully deleted trade {0}".format(id))
