from discord.ext.commands.core import is_owner
import twitter
import os
from dotenv import load_dotenv


load_dotenv()

# Keys and secrets can be get on https://developer.twitter.com/
# an account needs to be made

twitter = twitter.Api(
    consumer_key=os.getenv("Twitter_API_key"),
    consumer_secret=os.getenv("Twitter_API_secret"),
    access_token_key=os.getenv("Twitter_Access_token_key"),
    access_token_secret=os.getenv("Twitter_Access_token_secret"),
)


def user_by_id(id):
    try:
        user = twitter.GetUser(user_id=id)
        return {"tag": user.id_str, "name": user.name}
    except:
        return None


def user_by_screen_name(screen_name):
    try:
        user = twitter.GetUser(screen_name=screen_name)
        return {"tag": user.id_str, "name": user.name}
    except:
        return None


def get_user_info(account):
    # if account is id
    creator = user_by_id(account)
    if creator is not None:
        return creator

    # if account is id
    creator = user_by_screen_name(account)
    if creator is not None:
        return creator

    return None


def get_latest_tweet(id):
    user = twitter.GetUser(user_id=id)

    username = user.name
    link = f"https://twitter.com/{user.screen_name}/status/{user.status.id}"

    post = {"link": link, "username": username}
    return post
