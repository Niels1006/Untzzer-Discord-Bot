import json, random, discord

try:
    from main import UsefulMethods, Constants
except:
    import UsefulMethods, Constants


async def startup(bot):
    channel = UsefulMethods.getChannel(bot, "settings-selection")
    async for m in bot.logs_from(channel, limit=20):
        if m.author.id == bot.user.id:
            await bot.delete_message(m)

    await bot.send_file(channel, "data/reactionsSetup/settings.png")
    await bot.send_file(channel, "data/reactionsSetup/minibord.png")
    await bot.send_message(channel,
                           "**1- What games would you like to see? Press :x: to clear all roles.**")
    game_message = await bot.send_file(channel, "data/reactionsSetup/minisetting.png")

    for emoji in Constants.game_emojis:
        e = UsefulMethods.getEmoji(bot, emoji)
        await bot.add_reaction(game_message, e)
    await bot.add_reaction(game_message, UsefulMethods.getEmoji(bot, "delete_games"))

    await bot.send_file(channel, "data/reactionsSetup/minibord.png")
    platform_message = await bot.send_message(channel,
                                              "**2- What platform do you play on? Press :x: to clear all roles.**")

    for emoji in Constants.platform_emojis:
        e = UsefulMethods.getEmoji(bot, emoji)
        await bot.add_reaction(platform_message, e)
    await bot.add_reaction(platform_message, UsefulMethods.getEmoji(bot, "delete_platforms"))

    await bot.send_file(channel, "data/reactionsSetup/minibord.png")
    await bot.send_message(channel,
                           "**3- What notifications would you like to receive? Press :x: to clear all roles.**")
    notification_message = await bot.send_file(channel, "data/reactionsSetup/notifications.png")
    for emoji in Constants.notification_emojis:
        e = UsefulMethods.getEmoji(bot, emoji)
        await bot.add_reaction(notification_message, e)
    await bot.add_reaction(notification_message, UsefulMethods.getEmoji(bot, "delete_notifications"))

    await bot.send_file(channel, "data/reactionsSetup/minibord.png")
    await bot.send_message(channel, "For every 1 **partnership ping**, the participants are rewarded with 1 Mincoin :mincoin: \
                    Aiding us with partnerships will help this server grow and help us provide better content for you, help us help you!")


async def on_reaction_add(bot, reaction, user):
    if reaction.emoji.name in Constants.reactions and not user.bot:
        await bot.add_roles(user, UsefulMethods.getRole(user.server, reaction.emoji.name))
        await bot.send_message(user, "You successfully added {} to your profile!".format(reaction.emoji))

        await bot.remove_reaction(reaction.message, reaction.emoji, user)

    elif reaction.emoji.name.startswith("delete") and not user.bot:
        await bot.remove_reaction(reaction.message, reaction.emoji, user)

        for emoji in Constants.reaction_json[reaction.replace("delete_", "")]:
            while UsefulMethods.getRole(user.server, emoji) in user.roles:
                await bot.remove_roles(user, UsefulMethods.getRole(user.server, emoji))
