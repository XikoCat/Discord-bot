import configparser

import botUtils

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.app_commands import Choice

# Load configs
configs = configparser.ConfigParser()
configs.read("configs/bot.ini")
DEBUG_GUILD = configs.get("GENERAL", "debug_guild")

def is_owner():
    def predicate(it: Interaction) -> bool:
        return it.user.id == 102838147280293888
    return app_commands.check(predicate)

def cog_list():
    to_load = botUtils.loadable_cogs()
    cogs = []
    for cog in to_load:
        cogs.append(Choice(name=f'{cog}', value=f'{cog}'))
    return cogs

class Admin(commands.Cog, name="Admin commands"):
    """Admin-only commands that make the bot dynamic."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="load", description="Loads a cog")
    @is_owner()
    @app_commands.choices(cog = cog_list())
    async def load(self, it: Interaction, cog: Choice[str]):
        """Loads a module."""
        try:
            await self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await it.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await it.response.send_message("\N{OK HAND SIGN}")

    @app_commands.command(name="unload", description="Unload a cog")
    @is_owner()
    @app_commands.choices(cog = cog_list())
    async def unload(self, it: Interaction, cog: str):
        """Unloads a module."""
        try:
            await self.bot.unload_extension("cogs." + cog)
        except Exception as e:
            await it.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await it.response.send_message("\N{OK HAND SIGN}")

    @app_commands.command(name="reload", description="Reloads a cog")
    @is_owner()
    @app_commands.choices(cog = cog_list())
    async def reload(self, it: Interaction, cog: str):
        """Reloads a module."""

        try:
            await self.bot.unload_extension("cogs." + cog)
            await self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await it.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await it.response.send_message("\N{OK HAND SIGN}")

    @app_commands.command(name="debug", description="Sends debug info to user")
    @is_owner()
    async def debug(self, it: Interaction):
        await it.user.send("{}".format(it.user.id))
        await it.response.send_message("\N{OK HAND SIGN}")
    
    @debug.error
    async def debug_error(self, it: Interaction, error: discord.DiscordException):
        await it.response.send_message('\N{SKULL}/n{}'.format(error))


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot), guilds=[discord.Object(id=DEBUG_GUILD)])

