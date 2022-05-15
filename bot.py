import configparser
import os
import nextcord
from nextcord.ext import commands

# Load configs
configs = configparser.ConfigParser()
configs.read("configs/bot.ini")

DISCORD_TOKEN = configs.get("GENERAL", "discord_token")
PREFIX = configs.get("GENERAL", "command_prefix")
if PREFIX is None:
    PREFIX = "!"
print(f"prefix: {PREFIX}")

# Load intents
intents = nextcord.Intents.all()
intents.members = True

# Initialize client
client = commands.Bot(command_prefix=PREFIX, intents=intents)
slash = nextcord.slash_command()


@client.event
async def on_ready():
    print("Running!\nActive in:")
    for guild in client.guilds:
        print(f" - {guild.id} | {guild.name} | Member Count : {guild.member_count}")


cogs = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        cogs.append(filename[:-3])

for cog in cogs:
    print(f"Checking if cog can be loaded: {cog}")
    cog_config = configparser.ConfigParser()
    cog_config.read(f"configs/{cog}.ini")
    if cog_config.get("GENERAL", "Active").find("true") == 0:
        print(f"Loading cog: {cog}")
        client.load_extension("cogs." + cog)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
