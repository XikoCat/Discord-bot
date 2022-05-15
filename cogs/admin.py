import inspect
from collections import Counter

import nextcord
from nextcord.ext import commands
from nextcord import Interaction

from .utils import checks


class Admin(commands.Cog, name="Admin commands"):
    """Admin-only commands that make the bot dynamic."""

    guilds = [524243523243868160, 778754130021187584]

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="load", description="[Owner] Load a cog", guild_ids=guilds
    )
    @commands.is_owner()
    async def load(self, interaction: Interaction, cog):
        """Loads a module."""
        try:
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await interaction.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await interaction.response.send_message("\N{OK HAND SIGN}")

    @nextcord.slash_command(
        name="unload", description="[Owner] Unload a cog", guild_ids=guilds
    )
    @commands.is_owner()
    async def unload(self, interaction: Interaction, cog):
        """Unloads a module."""
        try:
            self.bot.unload_extension("cogs." + cog)
        except Exception as e:
            await interaction.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await interaction.response.send_message("\N{OK HAND SIGN}")

    @nextcord.slash_command(
        name="reload", description="[Owner] Reload a cog", guild_ids=guilds
    )
    @commands.is_owner()
    async def _reload(self, interaction: Interaction, cog):
        """Reloads a module."""

        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await interaction.response.send_message(
                "\N{SKULL}\n{}: {}".format(type(e).__name__, e)
            )
        else:
            await interaction.response.send_message("\N{OK HAND SIGN}")

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
