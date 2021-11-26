from datetime import datetime

import discord
from discord.ext import commands, tasks
from discord.ext.commands.core import guild_only
from discord.utils import get
from tinydb.queries import where

from .utils import twitter_api, youtube_api, twitch_api
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

    @tasks.loop(minutes=1)
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

            # if post is different from the last saved
            if str(creator["last_read"]).find(post["link"]) == -1:
                print(f" - Found new post from {post['username']}: {post['link']}")

                # update last_read to new post
                self.content_creator.update(
                    {"last_read": post["link"]}, doc_ids=(creator.doc_id,)
                )

                # get all subscriptions to creator
                creator_subscription = self.subscription.search(
                    where("content_creator") == creator.doc_id
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
                    # TODO CUSTOM MESSAGE PER PLATFORM
                    if creator["social_platform"] == 1:
                        message = f" {post['username']} just tweeted:\n{post['link']}"
                        await guild_channel.send(message)
                    if creator["social_platform"] == 2:
                        message = f" {post['username']} just posted:\n{post['link']}"
                        await guild_channel.send(message)
                    if creator["social_platform"] == 3:
                        embed = discord.Embed(
                            title=f" {post['username']} is now live on Twitch!",
                            description=post['title'],
                            color=discord.Color.purple(),
                            url=post["link"]
                        )
                        embed.set_image(url=post["thumbnail_url"])
                        embed.add_field(name="Jogo", value=post["game_name"])
                        await guild_channel.send("@here")
                        await guild_channel.send(embed=embed)

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
        if platform == 3:
            return twitch_api.get_stream_info(account)
        # TODO ADD MORE PLATORMS

    async def getPlatformId(self, ctx, arg):
        # get platform
        platform = self.platform_list.search(where("name") == arg)
        self.debugPrint(f"Platform query: {platform}")
        if len(platform) == 0:
            err_msg = f"[err:1] Invalid platform: {arg}"
            self.debugPrint(err_msg)
            await ctx.send(err_msg)
            return None
        platform = platform.pop()
        # if platform is available
        if platform["available"] == False:
            err_msg = f"[err:2] Invalid platform: {arg}"
            self.debugPrint(err_msg)
            await ctx.send(err_msg)
            return None
        return platform.doc_id

    async def getCreator(self, ctx, platform_id, creator_info, createIfNone=False):
        creator = self.content_creator.search(
            (where("social_platform") == platform_id)
            & (where("name") == creator_info["name"])
        )
        if len(creator) == 0:
            if createIfNone:
                creator = {
                    "tag": creator_info["tag"],
                    "name": creator_info["name"],
                    "social_platform": platform_id,
                    "last_read": "never",
                }
                self.debugPrint(f"Inserting content_creator: {creator}")
                id = self.content_creator.insert(creator)
                return self.content_creator.get(doc_id=id)
            else:
                err_msg = "[err:6] Not subscribed to creator"
                self.debugPrint(err_msg)
                await ctx.send(err_msg)
                return None
        else:
            creator = creator.pop()
        self.debugPrint(f"Creator: {creator.doc_id} - {creator}")
        return creator

    async def getChannel(self, ctx, createIfNone=False):
        channel = self.discord_channel.search(
            (where("guild_id") == ctx.guild.id) & (where("id") == ctx.channel.id)
        )
        if len(channel) == 0:
            if createIfNone:
                channel = {
                    "guild_name": ctx.guild.name,
                    "guild_id": ctx.guild.id,
                    "name": ctx.channel.name,
                    "id": ctx.channel.id,
                }
                self.debugPrint(f"Inserting discord_channel: {channel}")
                id = self.discord_channel.insert(channel)
                return self.discord_channel.get(doc_id=id)
            else:
                err_msg = f"[err:7] This channel is not subscribed to anything"
                self.debugPrint(err_msg)
                await ctx.send(err_msg)
                return None
        else:
            channel = channel.pop()
        self.debugPrint(f"Channel: {channel.doc_id} - {channel}")
        return channel

    def getSubscription(self, channel, creator):
        subscription = self.subscription.search(
            (where("discord_channel") == channel.doc_id)
            & (where("content_creator") == creator.doc_id)
        )
        if len(subscription) != 0:
            subscription = subscription.pop()
            self.debugPrint(f"subscription: {subscription.doc_id} - {subscription}")
            return subscription
        else:
            return None

    async def setSubscription(self, ctx, channel, creator):
        subscription = self.getSubscription(channel, creator)
        if subscription is None:
            subscription = {
                "discord_channel": channel.doc_id,
                "content_creator": creator.doc_id,
            }
            self.debugPrint(f"Inserting subscription: {subscription}")
            subscription_id = self.subscription.insert(subscription)
            self.debugPrint(f"subscription_id: {subscription_id}")
            return subscription
        else:
            err_msg = f"[err:4] - This channel is already subscribed to that creator"
            self.debugPrint(err_msg)
            await ctx.send(err_msg)
            return None

    async def getCreatorInfo(self, ctx, platform_id, creator_arg):
        # TODO Add more platforms
        self.debugPrint(f"Getting Creator Info of {creator_arg} on platform id {platform_id}")
        # if creator exists on twitter
        if platform_id == 1:
            creator_info = twitter_api.get_user_info(creator_arg)
        # if creator exists on youtube
        if platform_id == 2:
            creator_info = youtube_api.get_channel_info(creator_arg)
        # if creator exists on twitch
        if platform_id == 3:
            creator_info = twitch_api.get_user_info(creator_arg)
            self.debugPrint(f"creator_info: {creator_info}")
            if creator_info is None:
                err_msg = f"[err:3a] Invalid user: {creator_arg}"
                self.debugPrint(err_msg)
                await ctx.send(err_msg)
                return None
        return creator_info

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

        # get platform info if platform is available
        platform_id = await self.getPlatformId(ctx, platform_arg)
        self.debugPrint(f"Platform id: {platform_id}")
        if platform_id is None:
            return

        # get creator info if it exists on platform
        creator_info = await self.getCreatorInfo(ctx, platform_id, creator_arg)
        self.debugPrint(f"creator_info: {creator_info}")
        if creator_info is None:
            return

        # get or create creator on database
        creator = await self.getCreator(
            ctx, platform_id, creator_info, createIfNone=True
        )
        self.debugPrint(f"creator: {creator}")
        if creator is None:
            return

        # get or create channel on database
        channel = await self.getChannel(ctx, createIfNone=True)
        self.debugPrint(f"channel: {channel}")
        if channel is None:
            return

        # create subscription on datbase
        subscription = await self.setSubscription(ctx, channel, creator)
        self.debugPrint(f"subscription: {subscription}")
        if subscription is None:
            return

        await ctx.send(
            f"Success! Subscribed channel to {platform_arg} user: {creator['name']}"
        )
        await self.check_creator_posts()

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

        # get creator
        platform_id = await self.getPlatformId(ctx, platform_arg)
        creator_info = {"tag": None, "name": creator_arg}

        creator = await self.getCreator(
            ctx, platform_id, creator_info, createIfNone=False
        )
        self.debugPrint(f"creator: {creator}")
        if creator is None:
            return

        # get channel
        channel = await self.getChannel(ctx, createIfNone=False)
        self.debugPrint(f"channel: {channel}")
        if channel is None:
            return

        # get the subscription
        subscription = self.getSubscription(channel, creator)
        self.debugPrint(f"subscription: {subscription}")
        if subscription is None:
            err_msg = f"[err:8] This channel is not subscribed to that creator"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)

        # remove subscription
        print(subscription.doc_id)
        self.subscription.remove(doc_ids=(subscription.doc_id,))
        self.debugPrint(f"Subscription {subscription.doc_id} removed from database")

        # remove creator if no subscription needs it
        subs_for_creator = self.subscription.search(
            where("content_creator") == creator.doc_id
        )
        if len(subs_for_creator) == 0:
            self.content_creator.remove(doc_ids=(creator.doc_id,))
            self.debugPrint(
                f"Creator {creator.doc_id} - {creator} removed from database"
            )

        # remove channel if no subscription needs it
        subs_for_channel = self.subscription.search(
            where("discord_channel") == channel.doc_id
        )
        if len(subs_for_channel) == 0:
            self.discord_channel.remove(doc_ids=(channel.doc_id,))
            self.debugPrint(
                f"Channel {channel.doc_id} - {channel} removed from database"
            )

        await ctx.send(f"Success! Unsubscribed from {platform_arg} user: {creator_arg}")

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
        platforms = self.platform_list.search(where("available") == True)
        msg = "Currently available platforms:\n`"
        for p in platforms:
            name = p["name"]
            msg += f"{name}\n"
        msg += "`"
        await ctx.send(msg)

    @commands.command(name="show_subs", help="List all subscriptions on this channel")
    async def show_subs(self, ctx):
        # get channel
        channel = await self.getChannel(ctx, createIfNone=False)
        self.debugPrint(f"channel: {channel}")
        if channel is None:
            err_msg = "[err:10] Channel not subscribed to any content!"
            self.debugPrint(err_msg)
            return await ctx.send(err_msg)

        channel_subs = self.subscription.search(
            where("discord_channel") == channel.doc_id
        )

        msg = "Currently subscribed creators:\n`"

        for sub in channel_subs:
            creator = self.content_creator.get(doc_id=sub["content_creator"])
            name = creator["name"]

            plat = self.platform_list.get(doc_id=creator["social_platform"])["name"]
            msg += f"{plat} {name}\n"
        msg += "`"
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(cat_content_follow(bot))
