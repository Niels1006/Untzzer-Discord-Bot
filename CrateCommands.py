import json, random, discord

try:
    from main import UsefulMethods, Constants
except:
    import UsefulMethods, Constants


def loadCrateItems():
    with open("data/crate_items.json", "r") as f:
        return json.load(f)


def saveCrateItems(items):
    with open("data/crate_items.json", "w") as f:
        json.dump(items, f)


crates = ["regular", "golden", "diamond", "master"]
tiers = ["common", "uncommon", "rare", "epic", "legendary", "limited"]
coin_distribution = {"common": 1, "s.common": 3,
                     "uncommon": 2, "s.uncommon": 6,
                     "rare": 4, "s.rare": 12,
                     "epic": 8, "s.epic": 25,
                     "legendary": 16, "s.legendary": 50,
                     "limited": 32, "s.limited": 100}

percentages = {"regular": {"common": [55, 20],
                           "uncommon": [29, 15],
                           "rare": [13, 10],
                           "epic": [3, 7],
                           "legendary": [2, 5]},
               "golden": {"common": [38, 20],
                          "uncommon": [30, 15],
                          "rare": [20, 12],
                          "epic": [7, 10],
                          "legendary": [5, 7]},
               "diamond": {"common": [30, 20],
                           "uncommon": [27, 20],
                           "rare": [25, 15],
                           "epic": [10, 10],
                           "legendary": [8, 10]},
               "master": {"common": [0, 0],
                          "uncommon": [35, 20],
                          "rare": [30, 20],
                          "epic": [20, 20],
                          "legendary": [15, 20]}
               }


def reload_items():
    global items
    items = loadCrateItems()


reload_items()


def inventory(author, bot):
    data = openJSONCheck(author.id, author)
    crates = data["crates"][author.id]

    # crate_balance = "\u200b  Mincoin: {}\n".format(crates["minicoin"])
    crate_balance = "\u200b"

    if crates["regular"] > 0:
        crate_balance += "\u200b  Regular Crates: {}\n".format(crates["regular"])
    if crates["golden"] > 0:
        crate_balance += "\u200b  Golden Crates: {}\n".format(crates["golden"])
    if crates["diamond"] > 0:
        crate_balance += "\u200b  Diamond Crates: {}\n".format(crates["diamond"])
    if crates["master"] > 0:
        crate_balance += "\u200b  Master Crates: {}\n".format(crates["master"])

    if crate_balance == "\u200b":
        # crate_balance = "You don't have any crates."
        embed = UsefulMethods.buildBaseEmbed(author, "{0}'s Inventory".format(author.name))
    else:
        print("Hier!", crate_balance)

        embed = UsefulMethods.buildBaseEmbed(author, "{0}'s Inventory".format(author.name), crate_balance)

    embed.add_field(name="Mincoin", value="\u200b  {1} {0}\n".format(UsefulMethods.getAnimatedEmoji(bot, "mincoin"), crates["minicoin"]), inline = False)


    for r in tiers:
        out = ""
        for item in crates["items"][r]:
            shiny = ""
            shiny_bool = False
            item_out = item
            if crates["items"][r][item]["shiny"]:
                shiny = "**S.**"
                shiny_bool = True
                item_out = item[2:]

            amount = crates["items"][r][item]["am"]
            for _r in author.roles:
                if _r.name.lower() == item_out.lower():
                    print(checkIfShiny(_r))
                    if checkIfShiny(_r) == shiny_bool:
                        amount -= 1
            if not amount == 0:
                out_add = "\n\u200b {2}{0} x{1}".format(item_out.title(), amount, shiny)

                out += out_add
        if not out == "":
            embed.add_field(name="{} Roles".format(r.title()), value=out, inline=False)
    if out == "" and crate_balance == "":
        embed = UsefulMethods.buildBaseEmbed(author, "{0}'s Inventory".format(author.name), "This inventory is empty.")

    return embed


async def openCrate(bot, ctx, crate):
    crate = crate.lower()
    author = ctx.message.author
    if not crate in crates:
        return UsefulMethods.buildBaseEmbed(author, "Crate Opening", "Invalid Crate")
    data = openJSONCheck(author.id, author)

    if data["crates"][author.id][crate] > 0:
        data["crates"][author.id][crate] -= 1

        rarity = openCrate_Rarity(crate)

        item = random.choice(items[rarity])
        shiny = openCrate_Shiny(crate, rarity)
        shiny_msg = ""
        if shiny:
            shiny_msg = "***shiny*** "

        # data["crates"][author.id]["items"][rarity].append(item)
        addItemToInventory(item, shiny, data["crates"][author.id]["items"][rarity])

        saveJSON(data)
        # await bot.add_roles(author, UsefulMethods.getRole(ctx.message.server, winning))

        # role = discord.utils.find(lambda r: r.name == item, author.server.roles)
        roles = []
        colour = 0xFFFFFF
        for r in author.server.roles:
            if r.name.lower() == item.lower():
                roles.append(r)

        # print(shiny, "--------------------------------------------")

        if shiny:
            for r in roles:
                for p in r.permissions:
                    if ("change_nickname", True) == p:
                        colour = r.colour
        else:
            for r in roles:
                for p in r.permissions:
                    if ("change_nickname", False) == p:
                        print(r.name, r.colour)
                        colour = r.colour

        return UsefulMethods.buildBaseEmbed(author, "Crate Opening",
                                            "You got a(n) **{0}** role: {2}**{1}**!".format(rarity, item, shiny_msg),
                                            colour
                                            )
    else:
        return UsefulMethods.buildBaseEmbed(author, "Crate Opening", "You don't have enough crates!")


async def equip(bot, item, author):
    inv = openJSON()["crates"][author.id]["items"]
    shiny = False
    item_check = item
    if item.lower().startswith("s."):
        shiny = True
        item_check = item[2:]
    elif item.lower().startswith("shiny "):
        shiny = True
        item_check = item[6:]
        item = "Ss." + item[6:]

    if item.lower() == "mvp":
        item = "MVP"
    else:
        item = item.title()
    if not checkIfRoleExists(item_check):
        return UsefulMethods.buildBaseEmbed(author, "Crate System", "This role doesn't exist")
    try:
        for rarity in inv:
            for i in inv[rarity]:
                if i.lower() == item.lower():
                    if inv[rarity][item]["am"] >= 1 and inv[rarity][item]["shiny"] == shiny:
                        await bot.add_roles(author, getRole(author.server, i if not shiny else i[2:], shiny))
                        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                            "Equipped {}**{}** succesfully.".format(
                                                                "***shiny*** " if shiny else "", item))
    except IndentationError:
        return UsefulMethods.buildBaseEmbed(author, "Error", "Something went wrong, please dm {}. Thank you!".format(
            discord.utils.find(lambda u: u.id == Constants.ownerid, author.server.members).mention))

    return UsefulMethods.buildBaseEmbed(author, "Crate System", "You don't own this role.")


async def remove(bot, author, item):
    shiny = False
    if item.lower().startswith("s."):
        shiny = True
        item = item[2:]

    if not checkIfRoleExists(item) and not item.lower() == "all":
        return UsefulMethods.buildBaseEmbed(author, "Crate System", "This role isn't equippable")

    if any(r.name.lower() == item.lower() for r in author.roles):
        data = openJSONCheck(author.id, author)
        ########### SHINY BUG #################
        if item.title() not in data["crates"][author.id]["items"][getRarity(item)]:
            addItemToInventory(item.title(), shiny, data["crates"][author.id]["items"][getRarity(item)])
            saveJSON(data)

    if item.lower() == "all":
        roles = ""
        for role in author.roles:
            for r in tiers:
                for i in items[r]:
                    print(role.name.lower(), i.lower())
                    if role.name.lower() == i.lower():
                        while role in author.roles:
                            await bot.remove_roles(author, role)
                        roles += role.name + ", "
        if roles == "":
            return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                "You don't have any roles equipped.".format(roles[:-2]))
        else:
            return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                "Succesfully removed {}.".format(roles[:-2]))

    if shiny:
        for r in author.roles:
            if r.name.lower() == item.lower():
                for p in r.permissions:
                    if ("change_nickname", True) == p:
                        await bot.remove_roles(author, r)

                        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                            "Succesfully removed {}".format(item.title()))
    else:
        for r in author.roles:
            if r.name.lower() == item.lower():
                for p in r.permissions:
                    if ("change_nickname", False) == p:
                        await bot.remove_roles(author, r)
                        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                            "Succesfully removed {}".format(item.title()))

    return UsefulMethods.buildBaseEmbed(author, "Crate System", "You dont have this role equipped")


async def burn(bot, channel, author, kwargs):
    args = kwargs.lower().split(" ")
    print(args[0])
    # rarity
    if args[0] in tiers:
        duplicates = get_duplicated_roles_by_rarity(author, args[0])
        out = ""
        minicoin = 0
        for item in duplicates:
            minicoin += burn_item(author, item, duplicates[item])
            out += str(duplicates[item]) + " " + item + ", "

        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                            "You successfully burned {} and got {} Mincoins.".format(out[:-2],
                                                                                                     minicoin))

    if args[0].startswith("all"):
        duplicates = get_all_duplicated_roles(author)
        out = ""
        minicoin = 0
        for item in duplicates:
            minicoin += burn_item(author, item, duplicates[item])
            out += str(duplicates[item]) + " " + item + ", "

        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                            "You successfully burned {} and got {} Mincoins.".format(out[:-2],
                                                                                                     minicoin))

    amount = None
    for s in (list(kwargs)):
        if s.isdecimal():
            if amount:
                amount += s
            else:
                amount = s

    kwargs = kwargs.replace("" if amount is None else amount, "")[:(len(kwargs) if amount is None else -1)]
    print(kwargs + "A")

    if checkIfRoleExists(kwargs):
        if check_if_user_has_role(author, kwargs, 2 if amount is None else int(amount)):

            minicoin = 0

            amount = (1 if amount is None else int(amount))

            minicoin += burn_item(author, kwargs, 1 if amount is None else int(amount))
            out = str(amount) + " " + kwargs.title() + ", "

            if minicoin == 0:
                return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                    "You don't have multiple roles!")
            return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                "You successfully burned {} and got {} Mincoins.".format(out[:-2],
                                                                                                         minicoin))
        else:
            am_warnung = ("once" if amount is None else "{} times".format(amount))
            return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                                "You don't have this role more than {}.".format(am_warnung))
    return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                        "Invalid Arguments.")


def burn_item(author, item, amount):
    item = item.title()
    if item.lower().startswith("s."):
        item_normal = item[2:]
        print(item_normal)
    else:
        item_normal = item
    data = openJSONCheck(author.id, author)
    data["crates"][author.id]["minicoin"] += amount * coin_distribution[getRarity(item_normal)]
    data["crates"][author.id]["items"][getRarity(item_normal)][item]["am"] -= amount
    saveJSON(data)
    return amount * coin_distribution[getRarity(item_normal)]


def get_inv_items(author):
    return openJSONCheck(author.id, author)["crates"][author.id]["items"]


def get_all_duplicated_roles(author):
    inv = get_inv_items(author)
    duplicates = {}
    for _r in tiers:
        for r in inv[_r]:
            if inv[_r][r]["am"] > 1:
                duplicates[r] = inv[_r][r]["am"] - 1

    return duplicates


def get_duplicated_roles_by_rarity(author, _r):
    inv = get_inv_items(author)
    duplicates = {}
    for r in inv[_r]:
        if inv[_r][r]["am"] > 1:
            duplicates[r] = inv[_r][r]["am"] - 1

    return duplicates


def check_if_user_has_role(author, role, amount=1):
    inv = get_inv_items(author)
    if inv[getRarity(role.title())][role.title()]["am"] >= amount:
        return True
    return False


async def trade(bot, channel, author, receiver, roles):
    for i in range(30):
        if checkIfRoleExists(roles[:i]):
            item1 = roles[:i]
            item2 = roles[i + 1:]

    inv1 = openJSONCheck(author.id, author)["crates"][author.id]["items"]
    inv2 = openJSONCheck(receiver.id, receiver)["crates"][author.id]["items"]

    if not itemIsInInv(inv1, item1):
        return UsefulMethods.buildBaseEmbed(author, "Crate System", "You don't own this role.")
    if not itemIsInInv(inv2, item2):
        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                            "{} doesn't own this role.".format(receiver.mention))

    await bot.send_message(channel,
                           "You want to trade `{}` for `{}` with {}. Accept your trade with `yes`.".format(
                               item1.title(), item2.title(), receiver.mention))

    msg = await bot.wait_for_message(timeout=10, author=author, content="yes")

    if not msg:
        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                            "Canceled trade.".format(receiver.mention))

    await bot.send_message(channel,
                           "{2} please accept the trade with `yes`. You will get `{0}` for `{1}`".format(
                               item1.title(), item2.title(), receiver.mention))

    msg = await bot.wait_for_message(timeout=10, author=receiver, content="yes")
    if not msg:
        return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                            "Canceled trade.".format(receiver.mention))
    # receiver add
    addItemToInventory(item1)
    ########################### SHINY VERGESSEN SCHON GANZ OBEN!!!!!!!!!!!!!!!!!!!!!!!!!!

    return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                        "Succesfully traded {}'s {} for {}'s {}".format(author.mention, item1.title(),
                                                                                        receiver.mention,
                                                                                        item2.title()))


async def add_role(bot, author, rarity, item):
    if rarity not in tiers:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Rarity.")
    if not author.id in Constants.permissionLevel9000:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Permissions.")

    current_items = loadCrateItems()
    current_items[rarity].append(item)

    saveCrateItems(current_items)

    reload_items()

    return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                        "Succesfully added {} as a(n) {} role.".format(item, rarity))


async def show_roles(bot, author, rarity):
    roles = ""
    for r in items[rarity.lower()]:
        roles += "{} {} {}\n".format("\u200b", "\U000025CF", r)

    return UsefulMethods.buildBaseEmbed(author, "{} Roles".format(rarity.title()), roles)


async def give_crate(author, receiver, crate, amount):
    if not crate.lower() in crates:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Crate.")
    if not author.id in Constants.permissionLevel9000:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Permissions.")
    data = openJSONCheck(receiver.id, receiver)
    data["crates"][receiver.id][crate.lower()] += amount
    saveJSON(data)
    return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                        "Succesfully added {} {} crates to {} inventory.".format(amount, crate,
                                                                                                 receiver.mention))


async def remove_crate(author, receiver, crate, amount):
    if not crate.lower() in crates:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Crate.")
    if not author.id in Constants.permissionLevel9000:
        return UsefulMethods.buildBaseEmbed(author, "Crate System Error", "Invalid Permissions.")
    data = openJSONCheck(receiver.id, receiver)
    if data["crates"][receiver.id][crate.lower()] <= amount:
        amount = data["crates"][receiver.id][crate.lower()]
        data["crates"][receiver.id][crate.lower()] = 0
    else:
        data["crates"][receiver.id][crate.lower()] -= amount
    saveJSON(data)
    return UsefulMethods.buildBaseEmbed(author, "Crate System",
                                        "Succesfully removed {} {} crates from {} inventory.".format(amount, crate,
                                                                                                     receiver.mention))


async def removeAllCrateRoles(bot, author):
    for role in author.roles:
        for rarity in tiers:
            for name in items[rarity]:
                if role.name.lower() == name.lower():
                    await bot.remove_roles(author, role)


def getRole(server, name, shiny):
    if shiny:
        for r in server.roles:
            if r.name.lower() == name.lower():
                for p in r.permissions:
                    if ("change_nickname", True) == p:
                        return r
    else:
        for r in server.roles:
            if r.name.lower() == name.lower():
                for p in r.permissions:
                    if ("change_nickname", False) == p:
                        return r


def openCrate_Rarity(crate):
    percentage = random.randint(1, 100)
    if percentage <= percentages[crate]["common"][0]:
        return "common"
    elif percentage <= percentages[crate]["common"][0] + percentages[crate]["uncommon"][0]:
        return "uncommon"
    elif percentage <= percentages[crate]["common"][0] + percentages[crate]["uncommon"][0] + percentages[crate]["rare"][
        0]:
        return "rare"
    elif percentage <= percentages[crate]["common"][0] + percentages[crate]["uncommon"][0] + percentages[crate]["rare"][
        0] + \
            percentages[crate]["epic"][0]:
        return "epic"
    elif percentage <= percentages[crate]["common"][0] + percentages[crate]["uncommon"][0] + percentages[crate]["rare"][
        0] + \
            percentages[crate]["epic"][0] + percentages[crate]["legendary"][0]:
        return "legendary"


def checkIfShiny(role):
    for p in role.permissions:
        if ("change_nickname", True) == p:
            return True
    return False


def checkIfRoleExists(name):
    for r in tiers:
        for i in items[r]:
            if name.lower() == i.lower():
                return True
    return False


def openCrate_Shiny(crate, rarity):
    percentage = random.randint(1, 100)
    if percentage <= percentages[crate][rarity][1]:
        return True
    return False


def addItemToInventory(item, shiny, inv):
    def addNew():
        shiny_msg = ""
        if shiny:
            shiny_msg = "S."

        inv[shiny_msg + item] = {"am": 1,
                                 "shiny": shiny}

    if item in inv:
        if inv[item]["shiny"] == shiny:
            inv[item]["am"] += 1
        else:
            addNew()
    else:
        addNew()


def itemIsInInv(inv, name):
    for r in tiers:
        for i in inv[r]:
            if i.lower() == name.lower():
                return True

    return False


def getRarity(item):
    for r in tiers:
        for i in items[r]:
            if i.lower() == item.lower():
                return r


def openJSONCheck(id, author):
    data = openJSON()
    try:
        data["crates"][id]["minicoin"]
        data["crates"][id]
    except:
        data["crates"][id] = {"minicoin": 0,
                              "regular": 0,
                              "golden": 0,
                              "diamond": 0,
                              "master": 0,
                              "username": author.name,
                              "items": {"common": {},
                                        "uncommon": {},
                                        "rare": {},
                                        "epic": {},
                                        "limited": {},
                                        "legendary": {}}
                              }

        saveJSON(data)
    return data


def openJSON():
    with open("data/userinfos.json", "r") as f:
        return json.load(f)


def saveJSON(data):
    with open("data/userinfos.json", "w") as f:
        json.dump(data, f)
