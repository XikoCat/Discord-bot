import configparser
import discord
import requests
from discord.ext import commands, tasks

configs = configparser.ConfigParser()
configs.read("configs/mc_server.ini")

class cat_mc_server(commands.Cog, name="Minecraft server control"):
    def __init__(self, bot):
        self.bot = bot
        self.wait_time = int(configs.get('GENERAL', 'Idle_minutes'))
        self.time = 0
        self.current = 0

        self.on_minute.start()

    def cog_unload(self):
        self.on_minute.cancel()

    @tasks.loop(minutes=1)
    async def on_minute(self):
        if self.time > 0:
            self.time -= 1
        if self.request_server("state").find("starting") == 0:
            self.time = self.wait_time
        if self.request_server("state").find("on") == 0:
            players_list = self.request_server("list")
            players_on = int(players_list.split(" ")[2].split("/")[0])
            if players_on > 0:
                self.time = self.wait_time
            print(f"Players on: {players_on}, Staying on for {self.time} minutes")

            if self.time == 0:
                self.request_server("stop")
                print("Stopping the server!")

    @on_minute.before_loop
    async def before_on_minute(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name="mc",
        help="Minecraft server info",
    )
    async def mc(self, ctx):
        return await self.server_info(ctx)

    @commands.command(
        name="mc_start",
        help="Start the minecraft server",
    )
    async def mc_start(self, ctx):
        state = self.request_server("state")

        if state.find("on") == 0:
            self.time = self.wait_time
            await ctx.send(
                f"Server is already on\n Reseting shutdown timer ({self.wait_time} mins)"
            )

        if state.find("starting") == 0:
            await ctx.send("Server is already starting")

        if state.find("off") == 0:
            self.time = self.wait_time
            self.request_server("start")
            await ctx.send("Starting the server")

        return await self.server_info(ctx)

    @commands.command(
        name="mc_change",
        help="Change the server",
    )
    async def mc_change(self, ctx):
        state = self.request_server("state")

        if state.find("on") == 0:
            await ctx.send(
                "[Error] Can't change the server while it's on"
            )

        if state.find("starting") == 0:
            await ctx.send("[Error] Can't change the server while it's starting")

        if state.find("off") == 0:
            self.current = (self.current + 1)
            if not configs.has_section(f"MC_SERVER_{self.current}"):
                self.current = 0
            await ctx.send("Changed server")

        return await self.server_info(ctx)


    @commands.command(
        name="mc_stop",
        help="(Admin Only) Stop the minecraft server",
        hidden=False,
    )
    @commands.is_owner()
    async def mc_stop(self, ctx):
        state = self.request_server("state")

        if state.find("on") == 0:
            self.request_server("stop")
            await ctx.send(f"Stopping the server")

        if state.find("starting") == 0:
            await ctx.send(
                "Server is starting\nPlease wait until the server is on to stop it"
            )

        if state.find("off") == 0:
            await ctx.send("Server is already off")

        return await self.server_info(ctx)

    def request_server(self, arg):
        rcon = configs.get(f"MC_SERVER_{self.current}", 'Rcon_IP')
        answ = requests.get(f"{rcon}/{arg}")
        if answ.status_code == 200:
            return answ.text
        print(f"Got error code {answ.status.code}\n")

    async def server_info(self, ctx):
        public_ip = configs.get(f"MC_SERVER_{self.current}", 'Server_public_ip')
        pack = configs.get(f"MC_SERVER_{self.current}", 'Server_pack')
        pack_version = configs.get(f"MC_SERVER_{self.current}", 'Pack_version')
        pack_download_link = configs.get(f"MC_SERVER_{self.current}", 'Pack_Download_link')
        server_description = configs.get(f"MC_SERVER_{self.current}", 'Description')

        state = self.request_server("state")
        players_list = footer = None

        if state.find("on") == 0:
            players_list = self.request_server("list")

        if state.find("starting") == 0:
            footer = "Please hold a few minutes..."

        if state.find("off") == 0:
            footer = "To start the server please run '%mc_start'"

        embed = discord.Embed(
            title=f"Server Minecraft {pack}",
            description=server_description,
            color=discord.Color.green(),
        )
        # embed.set_image(url=f"{rcon}/icon")
        embed.add_field(name="IP", value=public_ip)
        embed.add_field(name="State", value=state, inline=True)
        if players_list is not None:
            embed.add_field(name="Players", value=players_list, inline=False)
        embed.add_field(name="modpack", value=pack_download_link, inline=False)
        embed.add_field(name="version", value=pack_version, inline=True)
        if footer is not None:
            embed.set_footer(text=footer)
        await ctx.send(embed=embed)

    # async def server_command(self, command):
    # TODO
        

def setup(bot):
    bot.add_cog(cat_mc_server(bot))
