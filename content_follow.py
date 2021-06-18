import discord
from discord.ext import commands
from datetime import datetime

class cat_content_follow(commands.Cog, name="Content Follow"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(cat_content_follow(bot))