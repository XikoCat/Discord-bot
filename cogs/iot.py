import discord
from discord.ext import commands

from .utils import tuya


class cat_iot(commands.Cog, name="IoT"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="light", help="Change light color")
    async def light(self, ctx, arg1, arg2=None, arg3=None):
        if str(arg1).find("on") != -1:
            tuya.device_turn_on(tuya.devices[0])
            return
        if str(arg1).find("off") != -1:
            tuya.device_turn_off(tuya.devices[0])
            return
        if str(arg1).find("white") != -1:
            tuya.bulb_white(tuya.devices[0])
            return
        tuya.bulb_color(tuya.devices[0], int(arg1), int(arg2), int(arg3))

    @commands.is_owner()
    @commands.command(name="fan", help="fan control")
    async def fan(self, ctx, arg1):
        if str(arg1).find("on") != -1:
            tuya.device_turn_on(tuya.devices[1])
            return
        if str(arg1).find("off") != -1:
            tuya.device_turn_off(tuya.devices[1])
            return


def setup(bot):
    bot.add_cog(cat_iot(bot))
