import configparser
import random

import discord
from discord import app_commands
from discord.ext import commands

# Load configs
configs = configparser.ConfigParser()
configs.read("configs/bot.ini")
DEBUG_GUILD = configs.get("GENERAL", "debug_guild")


class Fun(commands.Cog, name="Fun"):
    """Fun commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="battle", description="Battle another user")
    async def battle(
        self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        if interaction.user == user:
            return await interaction.response.send_message("Don't battle yourself!")
        winner = interaction.user if random.randint(0, 1) == 0 else user
        return await interaction.response.send_message(
            f"{winner.mention} won the battle!!!"
        )

    @app_commands.command(
        name="doilove", description="Find out how compatible are you with another user"
    )
    async def doilove(self, interaction: discord.Interaction, user: discord.User):
        lovemeter = (69 - (interaction.user.id + user.id) % 69 + 4) % 11
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
        await interaction.response.send_message(msg.format(user.mention))


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot), guilds=[discord.Object(id=DEBUG_GUILD)])
