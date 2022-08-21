import configparser
import os
import discord
from discord.ext import commands
import botUtils

# Load configs
configs = configparser.ConfigParser()
configs.read("configs/bot.ini")

DISCORD_TOKEN = configs.get("GENERAL", "discord_token")
PREFIX = configs.get("GENERAL", "command_prefix")
if PREFIX is None:
    PREFIX = "!"
print(f"prefix: {PREFIX}")
APPLICATION_ID = configs.get("GENERAL", "application_id")
DEBUG_GUILD = configs.get("GENERAL", "debug_guild")


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            # help_command=help_command,
            # tree_cls,
            # description,
            intents=discord.Intents.all(),
            application_id=APPLICATION_ID,
        )

    async def setup_hook(self):
        await self.load_extensions()
        await bot.tree.sync(guild=discord.Object(id=DEBUG_GUILD))

    async def on_ready(self):
        print("Running!\nActive in:")
        for guild in bot.guilds:
            print(f" - {guild.id} | {guild.name} | Member Count : {guild.member_count}")

    async def load_extensions(self):
        to_load = botUtils.loadable_cogs()
        for cog in to_load:
            print(f"Loading cog: {cog}")
            await self.load_extension(f"cogs.{cog}")


bot = MyBot()
bot.run(DISCORD_TOKEN)
