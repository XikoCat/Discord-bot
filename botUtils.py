import configparser
import os


def loadable_cogs():
        cogs = []
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cogs.append(filename[:-3])

        to_load = []
        for cog in cogs:
            cog_config = configparser.ConfigParser()
            cog_config.read(f"configs/{cog}.ini")
            if cog_config.get("GENERAL", "Active").find("true") == 0:
                to_load.append(f"{cog}")

        return to_load

            