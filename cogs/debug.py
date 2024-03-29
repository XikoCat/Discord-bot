from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands, Interaction


class Debug(commands.Cog, name="Debug commands"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tell_me_about_yourself(self, ctx):
        print(
            f"[{datetime.now()}] Command Issued: tell_me_about_yourself\n   - message: {ctx.message.content}\n   - debug: {ctx.message}"
        )

        text = "My name is XikoBot!\n. My creator is XikoCat. Check him out on twitter: https://twitter.com/xikocat\nType %help, to get a list of commands.\n :)"
        await ctx.send(text)

    @commands.command(help="Prints details of Author")
    async def whats_my_name(self, ctx):
        print(
            f"[{datetime.now()}] Command Issued: whats_my_name\n   - message: {ctx.message.content}\n   - debug: {ctx.message}"
        )
        await ctx.send(f"Hello {ctx.author.name}")

    @commands.command(help="Prints details of Server")
    async def where_am_i(self, ctx):
        print(
            f"[{datetime.now()}] Command Issued: where_am_i\n   - message: {ctx.message.content}\n   - debug: {ctx.message}"
        )
        owner = str(ctx.guild.owner)
        region = str(ctx.guild.region)
        guild_id = str(ctx.guild.id)
        memberCount = str(ctx.guild.member_count)
        icon = str(ctx.guild.icon_url)
        desc = ctx.guild.description

        embed = discord.Embed(
            title=ctx.guild.name + " Server Information",
            description=desc,
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Server ID", value=guild_id, inline=True)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Member Count", value=memberCount, inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Debug(bot))
