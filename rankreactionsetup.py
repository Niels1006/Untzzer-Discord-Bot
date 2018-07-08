try:
    from main import UsefulMethods
except:
    import UsefulMethods


async def rankreactionsetup(bot):
    for s in bot.servers:
        for c in s.channels:
            if c.name == "rules-and-roles":
                async for m in bot.logs_from(c, limit=10):
                    if m.content.startswith("Please select your platform."):
                        await bot.delete_message(m)
                msg = await bot.send_message(c,
                                             "Please select your platform. React with :x: to clear all your platform roles.")
                for e in ["pc", "ps4", "1xbox", "switch"]:
                    await bot.add_reaction(msg, UsefulMethods.getEmoji(bot, e))
                await bot.add_reaction(msg, "\U0000274C")
