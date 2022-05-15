import configparser
from contextvars import Context
from email import message
from shelve import Shelf

configs = configparser.ConfigParser()
configs.read("configs/shoutout.ini")

import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import Context

from .utils.json_db import db
from tinydb.table import Document
from tinydb import where


class shoutout(commands.Cog, name="Shoutout"):
    """Documentation"""

    guilds = [524243523243868160, 778754130021187584]

    def __init__(self, client):
        self.client = client
        # Database
        self.shouts = db.table("shouts")

    @commands.command()
    async def add_shout(self, ctx: Context):
        shout = {"message": ctx.message.content[11:], "triggers": []}
        doc_id = self.shouts.insert(shout)
        await ctx.message.reply(
            "Message added with id {}\nto add triggers do /add_trigger {} <trigger>".format(
                doc_id, doc_id
            )
        )

    @commands.command()
    async def add_trigger(self, ctx: Context, arg1):
        shout = self.shouts.get(doc_id=arg1)
        shout["triggers"].append(ctx.message.content.split(" ")[2])
        self.shouts.upsert(Document(shout, doc_id=arg1))
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def list_shouts(self, ctx: Context):
        shouts = self.shouts.all()
        m = ""
        for s in shouts:
            m += "{}: {}\n".format(s.doc_id, s["message"])
            for t in s["triggers"]:
                m += "    {}\n".format(t)
        if len(m) == 0:
            m = "There are no shouts configured"
        await ctx.message.reply(m)

    @commands.command()
    async def remove_shout(self, ctx: Context, arg1):
        shout = self.shouts.get(doc_id=arg1)
        self.shouts.remove(where("message") == shout["message"])
        await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        shouts = self.shouts.all()
        print(message.content)
        for s in shouts:
            for t in s["triggers"]:
                t = str(t).lower()
                m = str(message.content).lower()
                if t in m:
                    i = m.find(t)
                    l = len(t)
                    if i > 0:
                        if m[i - 1] != " ":
                            return
                    if i + l < len(m):
                        if m[i + l] != " ":
                            return
                    await message.channel.send(s["message"])
                    return


def setup(bot):
    bot.add_cog(shoutout(bot))
