try:
    from main import UsefulMethods as um, Constants
except:
    import UsefulMethods as um, Constants


async def clear(bot, author, channel, number):
    number = 100 if number > 100 else number
    for role in author.roles:
        if role.name in Constants.permissionLevel1 or author.id == Constants.ownerid:
            await bot.purge_from(channel=channel, limit=number + 1)
            return um.buildBaseEmbed(author, ";clear", "Succesfully cleared {} messages.".format(number))
    return um.buildBaseEmbed(author, ";clear", "You don't have enough permissions to do this!")
