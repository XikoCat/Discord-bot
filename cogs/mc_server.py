import discord
from discord.ext import commands

class cat_mc_server(commands.Cog, name="Minecraft server control"):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(cat_mc_server(bot))