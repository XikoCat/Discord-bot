import random

from discord.ext import commands

class cat_fun(commands.Cog, name="Fun"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battle", help="Battle with another user")
    async def battle(self, ctx):
        print(
            "Command Issued: battle\n   - message: {}\n   - debug: {}".format(
                ctx.message.content, ctx.message
            )
        )
        if ctx.author.id == ctx.message.mentions[0].id:
            await ctx.send("Don't battle yourself!")
            return
        winner = (
            ctx.author.id if random.randint(0, 1) == 0 else ctx.message.mentions[0].id
        )
        await ctx.send(f"<@{winner}> won the battle!!!")

    ##unused
    @battle.error
    async def battle_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("I could not find that member... do `!battle @adversary`")
        else:
            await ctx.send(f"Erro ao iniciar a batalha: {error}")

    @commands.command(
        name="doilove", help="Find out how compatible are you with another user"
    )
    async def doilove(self, ctx):
        print(
            "Command Issued: doilove\n   - message: {}\n   - debug: {}".format(
                ctx.message.content, ctx.message
            )
        )
        if len(ctx.message.mentions) == 0:
            await ctx.send(
                "Yes you do! But WHO is the question... do `!doilove @person`"
            )
            return
        lovemeter = (
            69 - (ctx.message.author.id - ctx.message.mentions[0].id) % 69 + 4
        ) % 11
        red = lovemeter
        white = 10 - lovemeter
        msg = "<3 Love meter Ɛ> ["
        while red > 0:
            msg += f"❤️"
            red -= 1
        while white > 0:
            msg += f"🖤"
            white -= 1
        msg += "]"
        lovemeter = int(lovemeter / 2)
        if lovemeter == 0:
            msg += "\nJust not meant to be!"
        if lovemeter == 1:
            msg += "\nMaybe in another life..."
        if lovemeter == 2:
            msg += "\nYou're better of as friends."
        if lovemeter == 3:
            msg += "\nThis might just work out!"
        if lovemeter == 4 or lovemeter == 5:
            msg += "\nDamn, {} perfect for each other!!"
        await ctx.send(msg.format(ctx.message.mentions[0].display_name))


def setup(bot):
    bot.add_cog(cat_fun(bot))
