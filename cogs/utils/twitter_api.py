from discord.ext.commands.core import is_owner
import tweepy
import os
from dotenv import load_dotenv


load_dotenv()

# Keys and secrets can be get on https://developer.twitter.com/
# an account needs to be made

auth = tweepy.OAuthHandler(
    consumer_key=os.getenv("Twitter_API_key"),
    consumer_secret=os.getenv("Twitter_API_secret"),
)
auth.set_access_token(
    key=os.getenv("Twitter_Access_token_key"),
    secret=os.getenv("Twitter_Access_token_secret"),
)

api = tweepy.API(auth)


def get_user_info(account):
    try:
        return api.get_user(screen_name=account).id_str
    except:
        return None


def get_latest_tweet(id):
    user = api.get_user(user_id=id)

    username = user.name
    link = f"https://twitter.com/{user.screen_name}/status/{user.status.id}"

    post = {"link": link, "username": username}
    return post
