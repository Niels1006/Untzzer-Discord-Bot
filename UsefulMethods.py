import json, discord, time, datetime

try:
    from main import Constants

except:
    import Constants

timebetweenreps = 43200


def openREP():
    with open("data/rep.json", "r") as f:
        return json.load(f)


def saveREP(data):
    with open("data/rep.json", "w") as f:
        json.dump(data, f)


def getEmoji(bot, name):
    for s in bot.servers:
        for e in s.emojis:
            if e.name == name:
                return e

def getAnimatedEmoji(bot, name):
    e = getEmoji(bot, name)
    return "<a:{}:{}>".format(e.name, e.id)


def getChannel(bot, name):
    for s in bot.servers:
        for c in s.channels:
            if c.name == name:
                return c


def getRole(server, name):
    for r in server.roles:
        if r.name.lower() == name.lower():
            return r


def checkPerms(user, lvl):
    for r in user.roles:
        if r.name in lvl:
            return True
    return False


def buildBaseEmbed(author, title, description=None, colour=Constants.EmbedColour,
                   footer="Please report bugs to @SyntaxFehler#8423. Thank you:)"):
    # time.strftime("%c", time.gmtime())
    if description is None:
        return discord.Embed(colour=colour).set_author(name=title,
                                                       icon_url=author.avatar_url).set_footer(
            text=footer)
    else:
        return discord.Embed(colour=colour, description=description).set_author(name=title,
                                                                                icon_url=author.avatar_url).set_footer(
            text=footer)


def checkRepTime(user, reppee):
    with open("data/reptime.json", "r") as f:
        data = json.load(f)

    try:
        if round(time.time()) - data[user.name + user.discriminator][
            reppee.name + reppee.discriminator] > timebetweenreps:
            data[user.name + user.discriminator][reppee.name + reppee.discriminator] = round(time.time())
            with open("data/reptime.json", "w") as f:
                json.dump(data, f)
            return True
        else:
            return False

    except KeyError:
        try:
            data[user.name + user.discriminator][str(reppee.name + reppee.discriminator)] = round(time.time())
            with open("data/reptime.json", "w") as f:
                json.dump(data, f)
            return True
        except KeyError:
            data[user.name + user.discriminator] = {str(reppee.name + reppee.discriminator): round(time.time())}
            with open("data/reptime.json", "w") as f:
                json.dump(data, f)
            return True


def timeTillNextRep(user, reppee):
    with open("data/reptime.json", "r") as f:
        data = json.load(f)

    return time.strftime("%H:%M",
                         time.localtime(data[user.name + user.discriminator][
                                            str(reppee.name + reppee.discriminator)] + timebetweenreps))


def addREP(rep, user, description, author):
    data = openREP()

    if rep == "+rep":

        try:
            counter = 1
            for d in data[user.id]["+rep"]:
                counter += 1
            for d in data[user.id]["-rep"]:
                counter += 1
            data[user.id]["+rep"].append({
                "mention": user.mention,
                "name": user.name + "#" + user.discriminator,
                "description": description,
                "author": author.mention,
                "authorname": author.name + "#" + author.discriminator,
                "number": counter
            })
        except KeyError:
            data[user.id] = ({
                "+rep": [{
                    "mention": user.mention,
                    "name": user.name + "#" + user.discriminator,
                    "description": description,
                    "author": author.mention,
                    "authorname": author.name + "#" + author.discriminator,
                    "number": 1
                }],
                "-rep": []
            })
    elif rep == "-rep":
        try:
            counter = 1
            for d in data[user.id]["+rep"]:
                counter += 1
            for d in data[user.id]["-rep"]:
                counter += 1
            data[user.id]["-rep"].append({
                "mention": user.mention,
                "name": user.name + "#" + user.discriminator,
                "description": description,
                "author": author.mention,
                "authorname": author.name + "#" + author.discriminator,
                "number": counter
            })
        except KeyError:
            data[user.id] = ({
                "+rep": [],
                "-rep": [{
                    "mention": user.mention,
                    "name": user.name + "#" + user.discriminator,
                    "description": description,
                    "author": author.mention,
                    "authorname": author.name + "#" + author.discriminator,
                    "number": 1
                }],
            })
    saveREP(data)


def latestREPS(user, count=5):
    data = openREP()
    count = int(count)
    em = discord.Embed(colour=discord.Color.dark_red())
    em.set_author(name="{0}'s {1} latest reps".format(user, count), icon_url=user.avatar_url)
    try:
        plusrep = minusrep = 0
        last5 = "```css"
        for d in data[user.id]["+rep"]:
            plusrep += 1
        for d in data[user.id]["-rep"]:
            minusrep += int(1)
        for i in range(plusrep + minusrep - count + 1, plusrep + minusrep + 1):
            for d in data[user.id]["+rep"]:
                # print(d["number"], i, plusrep, minusrep, count)
                if d["number"] == i:
                    last5 += "\n+{0} ".format(i) + d["description"] + " | [{0}]".format(d["authorname"])
            for d in data[user.id]["-rep"]:
                print(d)
                if d["number"] == i:
                    last5 += "\n-{0} ".format(i) + d["description"] + " | [{0}]".format(d["authorname"])

        if last5 == "```css":
            last5 = "```"
        # Unique rep
        users = []
        reps = 0
        for d in data[user.id]["+rep"]:
            reps += 1
            if not d["authorname"] in users:
                users.append(d["authorname"])
        for d in data[user.id]["-rep"]:
            reps += 1
            if not d["authorname"] in users:
                users.append(d["authorname"])

        place = 1
        for id in data:
            print(id)
            if len(data[id]["+rep"]) - len(data[id]["-rep"]) > plusrep - minusrep:
                place += 1

        # Rankings

        em.add_field(name="Overview", value="Positive: **{0}** | Negative: {1}".format(plusrep, minusrep), inline=False)
        em.add_field(name="Latest 5 reps", value=last5 + "\n```", inline=False)
        em.add_field(name="Unique Reputation", value="**{0}** Reps from **{1}** Users".format(reps, len(users)),
                     inline=False)
        em.add_field(name="Ranking", value="{0}/{1}".format(place, len(data)), inline=False)

        em.set_footer(text=time.strftime("%c", time.gmtime()))


    except KeyError as e:
        print(e)
        em.add_field(name="Error", value="This user doesn't have any reps.")

    # em.set_footer(text=footer)

    return em


def deleteREP(user, number):
    data = openREP()
    reps = []
    try:
        for d in data[user.id]["+rep"]:
            if not d["number"] == number:
                reps.append(d)
        data[user.id]["+rep"] = reps

        del reps
        reps = []

        for d in data[user.id]["-rep"]:
            if not d["number"] == number:
                reps.append(d)
        data[user.id]["-rep"] = reps

        for d in data[user.id]["+rep"]:

            if d["number"] > number:
                d["number"] -= 1
        for d in data[user.id]["-rep"]:
            if d["number"] > number:
                d["number"] -= 1

        saveREP(data)
        return buildBaseEmbed(user, "Delete Rep",
                              "Succesfully deleted rep#{0} from {1}'s profile".format(number, user.mention))

    except KeyError:
        return buildBaseEmbed(user, "Delete Rep, Error", "Invalid ID: {0}".format(number, user.mention))


def repcooldown(user):
    with open("data/reptime.json", "r") as f:
        data = json.load(f)

    em = buildBaseEmbed(user, "Rep Cooldowns")
    delete = 0
    for d in data[user.name + user.discriminator]:
        if time.time() - data[user.name + user.discriminator][d] > timebetweenreps:
            delete += 1

    for i in range(delete):
        for d in data[user.name + user.discriminator]:
            if time.time() - data[user.name + user.discriminator][d] > timebetweenreps:
                del data[user.name + user.discriminator][d]
                break

    for d in data[user.name + user.discriminator]:
        em.add_field(name=d[:-4] + "#" + d[-4:], value="{0} hours.".format(
            round((int(data[user.name + user.discriminator][d]) - time.time() + timebetweenreps) / 360) / 10.0))

    with open("data/reptime.json", "w") as f:
        json.dump(data, f)

    return em


def help(author):
    emoji = "\U000025CF"
    em = buildBaseEmbed(author, "Help | Page 1/1")
    em.add_field(inline=False, name="Reputation System", value="\u200b {0} **+rep** @User description\n"
                                                               " {0} **-rep** @User description\n"
                                                               " {0} **!rep** @User\n"
                                                               " {0} **!reps** @User count\n"
                                                               " {0} **!deleterep** @User ID\n"
                                                               " {0} **!repcooldown** @User".format(emoji))
    em.add_field(inline=False, name="Middleman System",
                 value="\u200b {0} **!call** @TradePartner platform tradedescription\n"
                       " {0} **!yes** -> Accepts the trade\n"
                       " {0} **!cancel** -> Cancels the trade\n"
                       " {0} **!confirm** `ID`\n"
                       " {0} **!close** `ID`\n"
                       " {0} **!delete** `ID`\n"
                       " {0} **!gettrades** `@Middleman`\n"
                       " {0} **!gettrade** `ID`\n"
                       " {0} **!delete** `ID`".format(emoji))
    em.add_field(inline=False, name="Crate System", value="\u200b {0} **!inventory**\n"
                                                          " {0} **!open** `crate`\n"
                                                          " {0} **!inventory**\n"
                                                          " {0} **!inv**\n"
                                                          " {0} **!equip** `role`\n"
                                                          " {0} **!remove** `role/all`\n"
                                                          " {0} **!burn** `item` `amount`\n"
                                                          " {0} **!burn** `rarity/all`\n"
                                                          " {0} **!givec** `user` `crate` `amount`\n"
                                                          " {0} **!removec** `user` `crate` `amount`\n"
                                                          " {0} **!add_role** `rarity` `role`\n"
                                                          " {0} **!show_roles** `rarity`".format(
        emoji))
    em.add_field(inline=False, name="Moderation System", value="\u200b {0} **!del** `count`\n"
                                                               "  ".format(emoji))
    return em
