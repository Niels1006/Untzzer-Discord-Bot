import discord
from discord.ext import commands
import os, asyncio

try:
    from main import MiddlemanCommands, UsefulMethods, ModerationCommands, rankreactionsetup, Constants, FunCommands, \
        CrateCommands, Vanguard, image_text, reactions
except:
    import MiddlemanCommands, UsefulMethods, ModerationCommands, rankreactionsetup, Constants, FunCommands, \
        CrateCommands, Vanguard, image_text, reactions

bot = commands.Bot(command_prefix=["+", "-", "!"], description="Hey")
bot.remove_command('help')

op = ["213420388741283840", "95899230434000896"]
permittedchannels = ["396308058340589578", "306451761760043008"]


# rep                  #botspam


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    # await rankreactionsetup.rankreactionsetup(bot)
    await bot.change_presence(game=discord.Game(name="!help"))
    await Vanguard.checkForReset(bot)
    await reactions.startup(bot)


@bot.command(pass_context=True)
async def test(ctx):
    from main import UsefulMethods
    print(UsefulMethods.timeTillNextRep(ctx.message.author))


@bot.command(pass_context=True)
async def rep(ctx, user: discord.Member = None, *, description: str = None):
    if not ctx.message.content.split(" ", 1)[0].startswith("!") and ctx.message.channel.id in permittedchannels:
        if ctx.message.author == user:
            await bot.say(embed=UsefulMethods.buildBaseEmbed(user, "Adding Rep", "You can't add reps to yourself!"))
            return
        if UsefulMethods.checkRepTime(ctx.message.author, user):
            UsefulMethods.addREP(ctx.message.content.split(" ", 1)[0], user, description, ctx.message.author)
            await bot.say(embed=UsefulMethods.buildBaseEmbed(ctx.message.author, "Adding Rep",
                                                             "Succesfully added to {0}'s profile. You can check your reps with `!rep`.".format(
                                                                 user.mention)))
        else:
            await bot.say(embed=UsefulMethods.buildBaseEmbed(ctx.message.author, "Adding Rep",
                                                             "You have to wait until {0} MEZ to post reps.".format(
                                                                 UsefulMethods.timeTillNextRep(ctx.message.author,
                                                                                               user))))
            pass
    if ctx.message.content.split(" ", 1)[0].startswith(
            "!") and ctx.message.channel.id in permittedchannels and description is None:
        if user is None:
            user = ctx.message.author
        await bot.say(embed=UsefulMethods.latestREPS(user))


@bot.command(pass_context=True)
async def reps(ctx, user: discord.Member, count=None):
    if ctx.message.content.split(" ", 1)[0].startswith("!") and ctx.message.channel.id in permittedchannels:
        if count == "all":
            count = 100
        await bot.say(embed=UsefulMethods.latestREPS(user, count))


@bot.command(pass_context=True)
async def deleterep(ctx, user: discord.Member, number: int):
    if ctx.message.channel.id in permittedchannels:
        if ctx.message.author.id in op:
            await bot.say(embed=UsefulMethods.deleteREP(user, number))
        else:
            await bot.say(embed=UsefulMethods.buildBaseEmbed(ctx.message.author, "Deleting Rep",
                                                             "You don't have enough permissions to do this."))


@bot.command(pass_context=True)
async def repcooldown(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.message.author
    await bot.say(embed=UsefulMethods.repcooldown(user))


@bot.command(pass_context=True)
async def call(ctx, trade_partner: discord.Member, platform: str, *, description: str):
    cmd = ctx.message.content.split(" ", 3)
    if not cmd[2].lower() in ["pc", "ps4", "xbox", "switch"]:
        await bot.say(embed=UsefulMethods.buildBaseEmbed(ctx.message.author, "Middleman System",
                                                         "Correct usage: **!call** `@TradePartner` `platform` `description`."))
        return
    await MiddlemanCommands.call(bot, ctx, trade_partner, platform, description)


@bot.command(pass_context=True)
async def yes(ctx):
    await MiddlemanCommands.yes(bot, ctx)


@bot.command(pass_context=True)
async def cancel(ctx):
    await MiddlemanCommands.cancel(bot, ctx)


@bot.command(pass_context=True)
async def confirm(ctx, id: str):
    await MiddlemanCommands.confirm(bot, ctx, id)


@bot.command(pass_context=True)
async def close(ctx, id: str):
    await bot.say(embed=await MiddlemanCommands.close(bot, ctx, id))


@bot.command(pass_context=True)
async def gettrades(ctx, mm: discord.Member):
    await bot.say(embed=await MiddlemanCommands.gettrades(ctx, mm))


@bot.command(pass_context=True)
async def gettrade(ctx, id: str = None):
    await bot.say(embed=await MiddlemanCommands.gettrade(ctx, id))


@bot.command(pass_context=True)
async def delete(ctx, id: str):
    await bot.say(embed=await MiddlemanCommands.delete(ctx, id, bot))


@bot.command(pass_context=True, name="del")
async def delete(ctx, number: int):
    msg = await bot.say(embed=await ModerationCommands.clear(bot, ctx.message.author, ctx.message.channel, number))
    await asyncio.sleep(5)
    await bot.delete_message(msg)


@bot.command(pass_context=True)
async def help(ctx):
    if os.name == "nt":
        from main import UsefulMethods
    else:
        import UsefulMethods
    await bot.say(embed=UsefulMethods.help(ctx.message.author))


# Crates

@bot.command(pass_context=True)
async def inventory(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    await bot.say(embed=CrateCommands.inventory(member))


@bot.command(pass_context=True)
async def inv(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    await bot.say(embed=CrateCommands.inventory(member, bot))


@bot.command(pass_context=True)
async def open(ctx, crate: str):
    await bot.say(embed=await CrateCommands.openCrate(bot, ctx, crate))


@bot.command(pass_context=True)
async def equip(ctx, *, item: str):
    await bot.say(embed=await CrateCommands.equip(bot, item, ctx.message.author))


@bot.command(pass_context=True)
async def remove(ctx, *, item: str):
    await bot.say(embed=await CrateCommands.remove(bot, ctx.message.author, item))


@bot.command(pass_context=True)
async def burn(ctx, *, args):
    await bot.say(embed=await CrateCommands.burn(bot, ctx.message.channel, ctx.message.author, args))


@bot.command(pass_context=True)
async def trade(ctx, member: discord.Member, *, roles: str):
    await bot.say(embed=await CrateCommands.trade(bot, ctx.message.channel, ctx.message.author, member, roles))


@bot.command(pass_context=True)
async def add_role(ctx, rarity: str, *, item: str):
    await bot.say(embed=await CrateCommands.add_role(bot, ctx.message.author, rarity, item))


@bot.command(pass_context=True)
async def show_roles(ctx, rarity: str):
    await bot.say(embed=await CrateCommands.show_roles(bot, ctx.message.author, rarity))


@bot.command(pass_context=True)
async def givec(ctx, receiver: discord.Member, crate, amount: int):
    await bot.say(embed=await CrateCommands.give_crate(ctx.message.author, receiver, crate, amount))


@bot.command(pass_context=True)
async def removec(ctx, receiver: discord.Member, crate, amount: int):
    await bot.say(embed=await CrateCommands.remove_crate(ctx.message.author, receiver, crate, amount))


@bot.command(pass_context=True)
async def doggy(ctx):
    image_text.main()
    await bot.send_file(ctx.message.channel, "sample-out.png")


@bot.command(pass_context=True)
async def add_beta(ctx):
    out = ""
    for u in ctx.message.server.members:
        if not discord.utils.find(lambda r: r.name.lower() == "beta tester", u.roles) in u.roles and not u.bot:
            out += (u.name + "\n")
    await bot.say(out)


# FUN


@bot.command(pass_context=True)
async def say(ctx, *, text: str):
    await bot.delete_message(ctx.message)
    if UsefulMethods.checkPerms(ctx.message.author, Constants.permissionLevel3):
        await bot.say(text)


@bot.command(pass_context=True)
async def fight(ctx, member: discord.Member):
    await FunCommands.fight(bot, ctx, member)


# Moderation
@bot.command(pass_context=True)
async def kick(ctx, member: discord.Member):
    for p in ctx.message.author.server_permissions:
        if p == ("kick_members", True):
            await bot.kick(member)
            Vanguard.addPoints(ctx.message.author, "!kick", 1)


@bot.command(pass_context=True)
async def ban(ctx, member: discord.Member):
    for p in ctx.message.author.server_permissions:
        if p == ("ban_members", True):
            await bot.ban(member, 30)
            Vanguard.addPoints(ctx.message.author, "!ban", 1)


# VANGUARD

# @bot.command(pass_context=True)
# async def get_invite(ctx):
#     await bot.say(await Vanguard.get_invite(bot, ctx.message.author, ctx.message.channel))


@bot.group()
async def activity():
    pass


@activity.command(pass_context=True)
async def stats(ctx, member: discord.Member):
    await bot.say(embed=Vanguard.stats_embed(member)[0])


@activity.command(pass_context=True)
async def leaderboard(ctx):
    await bot.say(embed=Vanguard.leaderboard_mods(ctx.message.author))


@activity.command(pass_context=True)
async def users(ctx):
    await bot.say(embed=Vanguard.leaderboard_users(ctx.message.author))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel.name == "middleman-call":
        await bot.delete_message(message)
    if message.channel.name == "suggestions":
        for e in ["\U0001F44D", "\U0001F44E"]:
            await bot.add_reaction(message, e)

    # VANGUARD

    if message.author.bot is False:
        Vanguard.event_message(message)


@bot.event
async def on_reaction_add(reaction, user):
    await reactions.on_reaction_add(bot,reaction, user)


# if reaction.emoji == "\U0000274C":
#     for role in reaction.message.server.roles:
#         if role.name.lower() in ["pc", "ps4", "xbox", "switch"]:
#             await bot.remove_roles(user, role)
#     return
# if reaction.emoji.name.lower() in ["pc", "ps4", "xbox", "switch"] and not user.bot:
#     # print(reaction.emoji.name)
#     for role in reaction.message.server.roles:
#         if role.name.lower() == reaction.emoji.name:
#             print(role.name, reaction.emoji.name)
#             await bot.add_roles(user, role)


if os.name == "nt":
    bot.run("MjgwMzQxNjk2NDU2Mjk0NDAw.DSghmg.rUIDhz62eQkaPKYnh1vzzqp-YEQ")
else:
    bot.run("Mzk2MjQwMTE5ODYzOTY3NzQ1.DSejFg.gEr8ITSoPjWAXsep6V88btWWEgk")
