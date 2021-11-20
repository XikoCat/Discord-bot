from datetime import datetime
from logging import debug
from os import name

from discord.ext import commands, tasks
from discord.ext.commands.core import guild_only
from discord.utils import get
from tinydb.queries import Query

from .utils import twitter_api, youtube_api
from .utils.json_db import db


class cat_content_follow(commands.Cog, name="Content Follow"):
    """Documentation"""

    def __init__(self, bot):
        self.bot = bot
        self.debug = True

        # Database
        self.platform_list = db.table("social_platform")
        self.subscription = db.table("subscription")
        self.discord_channel = db.table("discord_channel")
        self.content_creator = db.table("content_creator")

        self.check_creator_posts.start()

    def cog_unload(self):
        self.check_creator_posts.cancel()

    def debugPrint(self, msg):
        if self.debug:
            print("   - " + msg)

    @tasks.loop(minutes=3)
    async def check_creator_posts(self):
        now = datetime.now()
        print(f"[{now}] Checking for new posts!")

        # get creator list
        creator_list = self.content_creator.all()

        for creator in creator_list:
            # self.debugPrint(f" Verifying: {creator.doc_id} - {creator}")

            p = self.platform_list.get(doc_id=creator["social_platform"])
            if not p["available"]:
                continue

            # get the latest post
            post = self.getPost(creator["social_platform"], creator["tag"])
            post_link = post["link"]
            post_username = post["username"]

            # if post is different from the last saved
            if str(creator["last_read"]).find(post_link) == -1:
                print(f" - Found new post from {post_username}: {post_link}")

                # update last_read to new post
                self.content_creator.update(
                    {"last_read": post_link}, doc_ids=(creator.doc_id,)
                )

                # get all subscriptions to creator
                creator_subscription = self.subscription.search(
                    Query().content_creator == creator.doc_id
                )

                for sub in creator_subscription:
                    # get the channel info for that subscription
                    channel = self.discord_channel.get(doc_id=sub["discord_channel"])
                    guild = get(self.bot.guilds, id=channel["guild_id"])
                    if guild is None:
                        self.debugPrint(
                            "[err:9] Invalid guild!! could have been deleted"
                        )
                        continue

                    guild_channel = get(guild.text_channels, id=channel["id"])
                    if guild_channel is None:
                        self.debugPrint(
                            "[err:10] Invalid text channel, could have been deleted"
                        )
                        continue

                    # broadcast to new post to channel
                    await guild_channel.send(
                        f" {post_username} just posted:\n{post_link}"
                    )

                    # Extra - verify channel and guild name
                    if channel["guild_name"].find(guild.name) == -1:
                        old_name = channel["guild_name"]
                        new_name = guild.name
                        self.debugPrint(
                            f"Updating guild name from: {old_name} to {new_name}"
                        )
                        channel["guild_name"] = guild.name
                        self.discord_channel.update(
                            {"guild_name": guild.name}, doc_ids=(channel.doc_id,)
                        )
                    if channel["name"].find(guild_channel.name) == -1:
                        old_name = channel["name"]
                        new_name = guild_channel.name
                        self.debugPrint(
                            f"Updating channel name on guild {guild.name} from: {old_name} to {new_name}"
                        )
                        channel["name"] = guild_channel.name
                        self.discord_channel.update(
                            {"name": guild_channel.name}, doc_ids=(channel.doc_id,)
                        )

        print("Checking complete!")

    @check_creator_posts.before_loop
    async def before_check_creator_posts(self):
        await self.bot.wait_until_ready()

    def getPost(self, platform, account):
        if platform == 1:
            return twitter_api.get_latest_tweet(account)
        if platform == 2:
            return youtube_api.get_latest_video(account)
        # TODO ADD MORE PLATORMS

    @commands.command(
        name="subscribe", help="Subscribe to content from other platforms"
    )
    async def subscribe(self, ctx, arg1, arg2):
        print(
            f"[{datetime.now()}] Command Issued: subscribe\n   - message: {ctx.message.content}\n   - debug: {ctx.message}"
        )

        platform_arg = str(arg1).lower()
        creator_arg = str(arg2)

        msg = f"Subscribing to {platform_arg} user: {creator_arg}, please hold..."
        self.debugPrint(msg)
        await ctx.send(msg)

        # verify if arguments checkout

        # get platform
        platform = self.platform_list.search(Query().name == platform_arg)
        if len(platform) == 0:
            err_msg = f"[err:1] Invalid platform: {platform_arg}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)
        platform = platform.pop()

        # if platform is available
        if platform["available"] == False:
            err_msg = f"[err:2] Invalid platform: {platform_arg}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)

        platform_id = platform.doc_id

        # if creator exists on twitter
        if platform_id == 1:
            creator_info = twitter_api.get_user_info(creator_arg)
            if creator_info is None:
                err_msg = f"[err:3a] Invalid twitter user: {creator_arg}"
                self.debugPrint(err_msg)
                return await ctx.send(err_msg)
        # if creator exists on youtube
        if platform_id == 2:
            creator_info = youtube_api.get_channel_info(creator_arg)
            if creator_info is None:
                err_msg = f"[err:3b] Invalid youtube channel: {creator_arg} \nTip: you can search by channel ID, channel Username, or channel Name"
                self.debugPrint(err_msg)
                return await ctx.send(err_msg)

        # TODO if content exists on other platforms

        # get or create creator
        q = Query()
        creator = self.content_creator.search(
            (q.social_platform == platform_id) & (q.tag == creator_info["tag"])
        )
        if len(creator) == 0:
            creator = {
                "tag": creator_info["tag"],
                "name": creator_info["name"],
                "social_platform": platform_id,
                "last_read": "never",
            }
            self.debugPrint(f"Inserting content_creator: {creator}")
            creator_id = self.content_creator.insert(creator)
        else:
            creator = creator.pop()
            creator_id = creator.doc_id
        self.debugPrint(f"Creator: {creator_id} - {creator}")

        # get or create channel
        q = Query()
        channel = self.discord_channel.search(
            (q.guild_id == ctx.guild.id) & (q.id == ctx.channel.id)
        )
        if len(channel) == 0:
            channel = {
                "guild_name": ctx.guild.name,
                "guild_id": ctx.guild.id,
                "name": ctx.channel.name,
                "id": ctx.channel.id,
            }
            self.debugPrint(f"Inserting discord_channel: {channel}")
            channel_id = self.discord_channel.insert(channel)
        else:
            channel = channel.pop()
            channel_id = channel.doc_id
        self.debugPrint(f"Channel: {channel_id} - {channel}")

        # get or create subscription
        # if subscription exists -> error
        q = Query()
        subscription = self.subscription.search(
            (q.discord_channel == channel_id) & (q.content_creator == creator_id)
        )
        if len(subscription) > 0:
            # error - already exists
            tag = creator["name"]
            err_msg = f"[err:4] - This channel is already subscribed to {tag}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)

        subscription = {
            "discord_channel": channel_id,
            "content_creator": creator_id,
        }
        self.debugPrint(f"Inserting subscription: {subscription}")
        subscription_id = self.subscription.insert(subscription)

        self.debugPrint(f"subscription_id: {subscription_id}")

        plat = self.platform_list.get(doc_id=creator["social_platform"])["name"]
        await ctx.send(f"Success! Subscribed channel to {plat} user: {creator['name']}")

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
        print(
            f"[{datetime.now()}] Command Issued: unsubscribe\n   - message: {ctx.message.content}\n   - debug: {ctx.message}"
        )

        platform_arg = str(arg1).lower()
        creator_arg = str(arg2)

        msg = f"Unsubscribing to {platform_arg} user: {creator_arg}, please hold..."
        self.debugPrint(msg)
        await ctx.send(msg)

        # get platform
        platform = self.platform_list.search(Query().name == platform_arg)
        if len(platform) == 0:
            err_msg = f"[err:5] Invalid platform: {platform_arg}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)
        platform = platform.pop()
        platform_id = platform.doc_id

        # get creator
        q = Query()
        creator = self.content_creator.search(
            (q.social_platform == platform_id) & (q.tag == creator_arg)
        )
        if len(creator) == 0:
            err_msg = f"[err:6] Not subscribed to creator: {creator_arg}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)
        creator = creator.pop()
        creator_id = creator.doc_id
        creator_name = creator["name"]
        self.debugPrint(f"Creator: {creator_id} - {creator}")

        # get channel
        q = Query()
        channel = self.discord_channel.search(
            (q.guild_id == ctx.guild.id) & (q.id == ctx.channel.id)
        )
        if len(channel) == 0:
            err_msg = f"[err:7] This channel is not subscribed to anything"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)
        channel = channel.pop()
        channel_id = channel.doc_id
        self.debugPrint(f"Channel: {channel_id} - {channel}")

        # get the subscription id of pair content-channel if it exists
        q = Query()
        subscription = self.subscription.search(
            (q.discord_channel == channel_id) & (q.content_creator == creator_id)
        )
        if len(subscription) == 0:
            # error - does not exist
            err_msg = f"[err:8] This channel is not subscribed user: {creator_arg} : {creator_name}"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)
        subscription = subscription.pop()
        subscription_id = subscription.doc_id
        self.debugPrint(f"Channel: {subscription_id} - {subscription}")

        # remove subscription
        self.subscription.remove(doc_ids=(subscription_id,))
        self.debugPrint(f"Subscription {subscription_id} removed from database")

        # remove creator if no subscription needs it
        subs_for_creator = self.subscription.search(
            Query().content_creator == creator_id
        )
        if len(subs_for_creator) == 0:
            self.content_creator.remove(doc_ids=(creator_id,))
            self.debugPrint(f"Creator {creator_id} - {creator} removed from database")

        # remove channel if no subscription needs it
        subs_for_channel = self.subscription.search(
            Query().discord_channel == channel_id
        )
        if len(subs_for_channel) == 0:
            self.discord_channel.remove(doc_ids=(channel_id,))
            self.debugPrint(f"Channel {channel_id} - {channel} removed from database")

        await ctx.send(
            f"Success! Unsubscribed from {platform_arg} user: {creator_arg} - {creator_name}"
        )

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
        platforms = self.platform_list.search(Query().available == True)
        msg = "Currently available platforms:\n`"
        for p in platforms:
            name = p["name"]
            msg += f"{name}\n"
        msg += "`"
        await ctx.send(msg)

    @commands.command(name="show_subs", help="List all subscriptions on this channel")
    async def show_subs(self, ctx):
        channel = self.discord_channel.get(
            (Query().guild_id == ctx.guild.id) & (Query().id == ctx.channel.id)
        )

        if channel is None:
            err_msg = "[err:10] Channel not subscribed to any content!"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)

        channel_subs = self.subscription.search(
            Query().discord_channel == channel.doc_id
        )

        msg = "Currently subscribed creators:\n`"

        for sub in channel_subs:
            creator = self.content_creator.get(doc_id=sub["content_creator"])
            name = creator["name"]
            tag = creator["tag"]

            plat = self.platform_list.get(doc_id=creator["social_platform"])["name"]
            msg += f"{plat} {tag} : {name}\n"
        msg += "`"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(cat_content_follow(bot))
