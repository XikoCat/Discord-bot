from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime
from threading import Thread
import time

import db
import content_twitter as ct_twitter


class cat_content_follow(commands.Cog, name="Content Follow"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot
        self.platform_list = db.query("SELECT * FROM platform WHERE available = '1'")
        self.receive_posts = True
        self.check_creator_posts.start()

    def cog_unload(self):
        self.check_creator_posts.cancel()

    def get_platform_id(self, platform):
        i = 0
        for p in self.platform_list:
            i = i + 1
            str(p).find(platform) != -1
            return i
        return -1

    @tasks.loop(seconds=60)
    async def check_creator_posts(self):
        creator_list = db.query("SELECT * FROM content_creator")
        for creator in creator_list:
            print(f"Verifying: {creator}")
            link = self.getPost(creator.platform, str(creator.tag).split("'")[1])
            if str(creator.last_read).find(str(link)) == -1:
                print(f" ->Found new post: {link}")
                db.insert(
                    f"UPDATE content_creator SET last_read = '{link}' WHERE content_creator.id = '{creator.id}'"
                )
                subs = db.query(
                    "SELECT channel.guild, channel.channel FROM subscription"
                    + " INNER JOIN channel ON subscription.channel = channel.id"
                    + f" WHERE subscription.content_creator = '{creator.id}'"
                )
                for sub in subs:
                    guild = get(self.bot.guilds, name=str(sub.guild).split("'")[1])
                    channel = get(
                        guild.text_channels, name=str(sub.channel).split("'")[1]
                    )
                    if channel is not None:
                        c_nome = str(creator.tag).split("'")[1]
                        await channel.send(f"{c_nome} posted:\n{link}")

    @check_creator_posts.before_loop
    async def before_check_creator_posts(self):
        await self.bot.wait_until_ready()

    def getPost(self, platform, account):
        if platform == 1:
            return ct_twitter.get_tweet(screen_name=account)
        # TODO ADD MORE PLATORMS

    @commands.command(
        name="subscribe", help="Subscribe to content from other platforms"
    )
    async def subscribe(self, ctx, arg1, arg2):
        platform = str(arg1).lower()
        account = str(arg2).lower()
        platform_id = self.get_platform_id(platform)

        # verify if arguments checkout
        # if platform is valid
        if platform_id == -1:
            return await ctx.send(f"Invalid platform: {platform}")

        # if content exists on platform
        if platform.find("twitter") != -1 and not ct_twitter.user_is_valid(account):
            return await ctx.send(f"Invalid twitter user: {account}")
        # TODO ADD OTHER PLATFORM VERIFICATIONS

        creator_id = db.query(
            f"SELECT * FROM content_creator WHERE platform = '{platform_id}' AND tag = '{account}'"
        )
        if len(creator_id) == 0:
            creator_id = db.insert(
                f"INSERT INTO content_creator (platform, tag, last_read) VALUES ({platform_id}, '{account}', 'NULL')"
            )
        else:
            creator_id = creator_id.pop().id

        channel_id = db.query(
            f"SELECT * FROM channel WHERE guild = '{ctx.guild}' AND channel = '{ctx.channel}'"
        )
        if len(channel_id) == 0:
            channel_id = db.insert(
                f"INSERT INTO channel (guild, channel) VALUES ('{ctx.guild}', '{ctx.channel}')"
            )
        else:
            channel_id = channel_id.pop().id

        sub_id = db.query(
            f"SELECT * FROM subscription WHERE channel = '{channel_id}' AND content_creator = '{creator_id}'"
        )
        if len(sub_id) != 0:
            print(
                f"{ctx.guild} - channel: {ctx.channel} was already subscribed to {platform} user: {account}"
            )
            return await ctx.send(
                f"Error: This channel was already subscribed to {platform} user: {account}"
            )

        db.insert(
            f"INSERT INTO subscription (channel, content_creator) VALUES ({channel_id}, {creator_id})"
        )
        await ctx.send(f"Success! Subscribing channel to {platform} user: {account}")

    @subscribe.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Invalid format! Type:\n"
                + "`%subscribe <platform> <account>`\n"
                + "For a list of available platforms type:\n"
                + "`%sub_platforms`"
            )

    @commands.command(name="unsubscribe", help="Unsubscribe to content")
    async def unsubscribe(self, ctx, arg1, arg2):
        platform = str(arg1).lower()
        account = str(arg2).lower()
        platform_id = self.get_platform_id(platform)

        await ctx.send(f"Unsubscribing {platform} user: {account}, please hold...")

        # if platform is valid
        if platform_id == -1:
            return await ctx.send(f"Invalid platform: {platform}")

        creator_id = db.query(
            f"SELECT * FROM content_creator WHERE platform = '{platform_id}' AND tag = '{account}'"
        )
        if len(creator_id) == 0:
            return await ctx.send(
                f"Error: This channel is not subscribed to {platform} user: {account}"
            )
        creator_id = creator_id.pop().id

        channel_id = db.query(
            f"SELECT * FROM channel WHERE guild = '{ctx.guild}' AND channel = '{ctx.channel}'"
        )
        if len(channel_id) == 0:
            return await ctx.send(f"Error: This channel is not subscribed to anything")
        channel_id = channel_id.pop().id

        sub_id = db.query(
            f"SELECT * FROM subscription WHERE channel = '{channel_id}' AND content_creator = '{creator_id}'"
        )
        if len(sub_id) < 1:
            print(
                f"{ctx.guild} - channel: {ctx.channel} is not subscribed to {platform} user: {account}"
            )
            return await ctx.send(
                f"Error: This channel is not subscribed to {platform} user: {account}"
            )
        sub_id = sub_id.pop().id

        db.insert(f"DELETE FROM subscription WHERE id = {sub_id}")
        await ctx.send(f"Success! Unsubscribed from {platform} user: {account}")

    @unsubscribe.error
    async def unsubscribe_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Invalid format! Type:\n"
                + "`%unsubscribe <platform> <account>`\n"
                + "For the list of current subscriptions type:\n"
                + "`%show_subs`\n"
            )

    @commands.command(name="sub_platforms", help="List all platforms available")
    async def sub_platforms(self, ctx):
        self.platform_list = db.query("SELECT * FROM platform WHERE available = '1'")
        msg = "Currently available platforms:\n`"
        for p in self.platform_list:
            name = str(p.name).split("'")[1]
            msg += f"{name}\n"
        msg += "`"
        await ctx.send(msg)

    @commands.command(name="show_subs", help="List all subscriptions on this channel")
    async def show_subs(self, ctx):
        gc_id = db.query(
            f"SELECT * FROM channel WHERE guild = '{ctx.guild}' AND channel = '{ctx.channel}'"
        )
        gc_id = gc_id.pop().id
        sub_list = db.query(
            f"SELECT content_creator.id, content_creator.platform, content_creator.tag, subscription.channel FROM subscription RIGHT JOIN content_creator ON subscription.content_creator = content_creator.id WHERE subscription.channel = '{gc_id}'"
        )

        msg = "Currently subscribed creators:\n`"
        for p in sub_list:
            plat = str(self.platform_list[p.platform - 1].name).split("'")[1]
            tag = str(p.tag).split("'")[1]
            msg += f"{plat}: {tag}\n"
        msg += "`"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(cat_content_follow(bot))
