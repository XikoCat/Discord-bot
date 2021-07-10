from discord.ext import commands
from .utils import checks
import inspect

from collections import Counter


class Admin(commands.Cog, name="Admin commands"):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, arg1):
        """Loads a module."""
        try:
            self.bot.load_extension(arg1)
        except Exception as e:
            await ctx.send("\N{SKULL}")
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, arg1):
        """Unloads a module."""
        try:
            self.bot.unload_extension(arg1)
        except Exception as e:
            await ctx.send("\N{SKULL}")
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, arg1):
        """Reloads a module."""

        try:
            self.bot.unload_extension(arg1)
            self.bot.load_extension(arg1)
        except Exception as e:
            await ctx.send("\N{SKULL}")
            await ctx.send("{}: {}".format(type(e).__name__, e))
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def debug(self, ctx, *, code: str):
        """Evaluates code."""
        code = code.strip("` ")
        python = "```py\n{}\n```"
        result = None

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "server": ctx.message.server,
            "channel": ctx.message.channel,
            "author": ctx.message.author,
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await self.bot.say(python.format(type(e).__name__ + ": " + str(e)))
            return

        await self.bot.say(python.format(result))


def setup(bot):
    bot.add_cog(Admin(bot))
