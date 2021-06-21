import discord
from discord.ext import commands
from datetime import datetime

import random

class cat_fun(commands.Cog, name="Fun"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot

    #######################################################################
    #############################          ################################
    #############################  BATTLE  ################################
    #############################          ################################
    #######################################################################


    @commands.command(name="battle", help="Battle with another user")
    async def battle(self, ctx):
        print(
            "Command Issued: battle\n   - message: {}\n   - debug: {}".format(
                ctx.message.content, ctx.message
            )
        )
        if ctx.author.id == ctx.message.mentions[0].id:
            await ctx.send("Don't battle yourself, you LONER!")
            return
        winner = ctx.author.id if random.randint(0, 1) == 0 else ctx.message.mentions[0].id
        await ctx.send(f"<@{winner}> has the biggest dick!!!")

    ##unused
    @battle.error
    async def battle_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("I could not find that member... do `!battle @adversary`")
        else:
            await ctx.send(f"A batalha fudeu: {error}")


    ######################################################################
    #############################         ################################
    ############################# DOILOVE ################################
    #############################         ################################
    ######################################################################


    @commands.command(name="doilove", help="Find out how compatible are you with another user")
    async def doilove(self, ctx):
        print(
            "Command Issued: doilove\n   - message: {}\n   - debug: {}".format(
                ctx.message.content, ctx.message
            )
        )
        if len(ctx.message.mentions) == 0:
            await ctx.send("Yes you do! But WHO is the question... do `!doilove @person`")
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
            msg += "\nA better romance than Crepusculo! 💔"
        if lovemeter == 1:
            msg += "\nYou don't need love, as long as there's a hole"
        if lovemeter == 2:
            msg += "\nMaybe with some effort... and dick picks"
        if lovemeter == 3:
            msg += "\nAs good as your hand!"
        if lovemeter == 4:
            msg += "\nDamn, {} must give you lots of wet dreams!!"
        if lovemeter == 5:
            msg += "\nDamn, {} must give you lots of wet dreams!!"
        await ctx.send(msg.format(ctx.message.mentions[0].display_name))



def setup(bot):
    bot.add_cog(cat_fun(bot))