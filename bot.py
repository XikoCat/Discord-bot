import configparser
import discord
from discord.ext import commands

configs = configparser.ConfigParser()
configs.read("configs/bot.ini")

DISCORD_TOKEN = configs.get("GENERAL", "discord_token")
PREFIX = configs.get("GENERAL", "command_prefix")
if PREFIX is None:
    PREFIX = "!"
print(f"prefix: {PREFIX}")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

cogs = ["admin", "content_follow", "debug", "fun", "iot", "mc_server", "nhentai"]
for cog in cogs:
    print(f"Checking if cog can be loaded: {cog}")
    cog_config = configparser.ConfigParser()
    cog_config.read(f"configs/{cog}.ini")
    if cog_config.get("GENERAL", "Active").find("true") == 0:
        print(f"Loading cog: {cog}")
        bot.load_extension("cogs." + cog)


@bot.event
async def on_ready():
    print("Running!\nActive in:")
    for guild in bot.guilds:
        print(f" - {guild.name} | Member Count : {guild.member_count}")


@bot.event
async def on_message(message):
    # bot.process_commands(msg) is a coroutine that must be called here since we are overriding the on_message event
    await bot.process_commands(message)
    
    message_string = str(message.content).lower()
    if message_string.find("tetr.io") != -1 or message_string.find("tetris") != -1:
        await message.channel.send(
            "Alguém falou em **T E T R I S**?\n⚡⚡⚡!!!Chamem o <@177524951035805697> para jogarem !!!⚡⚡⚡"
        )

    if message_string.find("caixa_nerd") != -1:
        await message.channel.send("já visitaram o site https://caixanerd.pt ?")
    if message_string.find("bolo") != -1:
        await message.channel.send(
            "https://media.discordapp.net/attachments/734800127927123989/883405449146294292/f49e5e27b7e4bdcf02816b5b19e51a6d.gif"
        )

    if message_string.find("rage") != -1:
        await message.channel.send(
            "https://media.discordapp.net/attachments/734800127927123989/893452560474714122/ezgif.com-gif-maker.gif"
        )
    if message_string.find("hype") != -1:
        await message.channel.send(
            "https://media.discordapp.net/attachments/734800127927123989/894964048540618832/ezgif.com-gif-maker3.gif"
        )

    # message_string = str(message.content).lower()
    # if message_string.find("tetr.io") != -1 or message_string.find("tetris") != -1:
    #    await message.channel.send(
    #        "Alguém falou em **T E T R I S**?\n⚡⚡⚡!!!Thunder!!!⚡⚡⚡"
    #    )

    # if message_string.find("moura") != -1:
    #    await message.channel.send(
    #        "Why!? Why would you bring that bloody cursed word upon this land!"
    #    )

    # if message_string in ["swear_word1", "swear_word2"]:
    #    await message.channel.purge(limit=1)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
