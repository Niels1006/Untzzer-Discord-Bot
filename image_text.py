try:
    from main import UsefulMethods, Constants, CrateCommands
except:
    import UsefulMethods, Constants, CrateCommands

import json, random, discord
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def main():
    img = Image.new("RGBA", (1000, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font = ImageFont.truetype("arial.ttf", 30)
    # draw.text((x, y),"Sample Text",(r,g,b))

    img.save('sample-out.png')  #


def createTransparentPicture():
    img = Image.new("RGBA", (1000, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return draw


def draw_inv(author, bot):
    draw = createTransparentPicture()
    font = ImageFont.truetype("arial.ttf", 30)

    data = CrateCommands.openJSONCheck(author.id, author)
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
        pass

    else:
        draw.text((100, 100), crate_balance, (255, 255, 255), font=font)

        embed = UsefulMethods.buildBaseEmbed(author, "{0}'s Inventory".format(author.name), crate_balance)

