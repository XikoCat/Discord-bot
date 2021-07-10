import discord
from discord.ext import commands, tasks

import os
from dotenv import load_dotenv

import subprocess

load_dotenv()

import time

from mcrcon import MCRcon


class cat_mc_server(commands.Cog, name="Minecraft server control"):
    def __init__(self, bot):
        self.bot = bot

        self.server = None
        self.server_started = False

        self.wait_time = 10  # time in minutes the server will be up with no one inside
        self.time = 0

        self.on_minute.start()

    def cog_unload(self):
        self.on_minute.cancel()

    def rcon(self, cmd):
        ip = os.getenv("MC_rcon_ip")
        secret = os.getenv("MC_rcon_secret")

        mcr = MCRcon(ip, secret)
        mcr.connect()
        resp = mcr.command(cmd)
        mcr.disconnect()

        return resp

    @tasks.loop(minutes=1)
    async def on_minute(self):
        if self.time > 0:
            self.time -= 1

        if self.server_started:
            players_list = self.rcon("/list")
            players_on = int(players_list.split(" ")[2])
            print(players_on)
            if players_on > 0:
                self.time = self.wait_time
            print(self.time)

            if self.time == 0:
                await self.server_command("stop")
                time.sleep(30)
                self.server.kill()
                self.server_started = False

    async def mc_help(self, ctx):
        msg = (
            "```Minecraft server control\n"
            + "\n"
            + "Usage %mc <arg>\n"
            + "\n"
            + "Options:\n"
            + "  help         Displays this message\n"
            + "  start        Starts the server, a message is sent once the server is fully started and ready to join.\n"
            + f"                  The server will stay up for {self.wait_time} minutes until someone joins.\n"
            + "  info         Displays some info about the server: ip, state, up time, players online\n"
            + "```"
        )
        return await ctx.send(msg)

    async def mc_info(self, ctx):
        public_ip = os.getenv("MC_Server_public_ip")
        pack = os.getenv("MC_Server_pack")
        pack_version = os.getenv("MC_Pack_version")
        pack_download_link = os.getenv("MC_Pack_Download_link")
        server_description = os.getenv("MC_Description")

        state = "OFF\n to turn on do:\n%mc start"
        if self.server_started:

            players_list = self.rcon("/list")

            players_count = int(players_list.split(" ")[2])

            temp_list = players_list.split(" ")

            players_on = ""
            for x in range(10, len(temp_list)):
                player = temp_list[x]
                players_on = players_on + f"- {player}"

            state = f"ON\nPlayers on: {players_count}\n{players_on}"

        msg = (
            f"```Minecraft {pack}\n"
            + f"Version: {pack_version}\n"
            + f"Download link: {pack_download_link}\n"
            + "\n"
            + f"IP: {public_ip}\n"
            + f"State: {state}\n"
            + "\n"
            + f"{server_description}\n"
            + "```"
        )
        return await ctx.send(msg)

    async def server_command(self, command):
        if self.server_started is False:
            return
        self.server.stdin.write((command + "\n").encode())
        self.server.stdin.flush()

    async def server_start(self, ctx):
        minecraft_dir = os.getenv("MC_Server_dir")
        server_jar = os.getenv("MC_Server_jar_file")
        minRam = os.getenv("MC_alloc_mem_min")
        maxRam = os.getenv("MC_alloc_mem_max")
        public_ip = os.getenv("MC_Server_public_ip")

        executable = f"java -Xms{minRam} -Xmx{maxRam} -jar {server_jar} nogui"
        if self.server_started:
            return await ctx.send("Sever is already STARTED")
        print(
            f"starting minecraft server - dir: {minecraft_dir} | executable: {executable}"
        )
        self.server = subprocess.Popen(
            executable, stdin=subprocess.PIPE, cwd=minecraft_dir, shell=True
        )
        self.server_started = True
        self.time = self.wait_time
        await ctx.send(
            f"Server is starting! IP: `{public_ip}`\n"
            + f"If no one joins within {self.wait_time} minutes the server will close"
        )

    async def server_stop(self, ctx, now=False):
        if self.server_started is False:
            return await ctx.send("Sever is already STOPPED")

        print("Server stopping...")

        if not now:
            await self.server_command("say The server is shutting down in 5 minutes!")
            time.sleep(240)  # wait 4 minutes
            await self.server_command("say The server is shutting down in 1 minute!")
            time.sleep(30)  # wait a few seconds in between messages
            await self.server_command("say The server is shutting down in 30 seconds!")
            time.sleep(20)  # wait a few seconds in between messages
            await self.server_command("say The server is shutting down in 10 seconds!")
            time.sleep(5)  # wait a few seconds in between messages
            await self.server_command("say The server is shutting down in 5 seconds!")
            time.sleep(5)  # wait a few seconds in between messages

        await self.server_command("stop")
        time.sleep(20)
        self.server.kill()
        time.sleep(10)  # wait 10 more seconds to let things cool down
        self.server_started = False

    @commands.command(
        name="mc_admin",
        help="Minecraft server control. %mc help for more info",
        hidden=True,
    )
    @commands.is_owner()
    async def mc_admin(self, ctx, arg1):
        arg1 = str(arg1).lower()

        if arg1.find("help") != -1:
            return await self.mc_help(ctx)

        if arg1.find("start") != -1:
            return await self.server_start(ctx)

        if arg1.find("stop") != -1:
            return await self.server_stop(ctx, now=True)

        if arg1.find("stats") != -1:
            return

        return await ctx.send(
            f'Invalid argument "{arg1}"\nType `%mc help` for a list of options'
        )

    @mc_admin.error
    async def mc_admin_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.mc_help(ctx)

    @commands.command(
        name="mc",
        help="Minecraft server control. %mc help for more info",
    )
    async def mc(self, ctx, arg1):
        arg1 = str(arg1).lower()

        if arg1.find("help") != -1:
            return await self.mc_help(ctx)

        if arg1.find("start") != -1:
            return await self.server_start(ctx)

        if arg1.find("info") != -1:
            return await self.mc_info(ctx)

        return await ctx.send(
            f'Invalid argument "{arg1}"\nType `%mc help` for a list of options'
        )

    @mc.error
    async def mc_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.mc_help(ctx)


def setup(bot):
    bot.add_cog(cat_mc_server(bot))
