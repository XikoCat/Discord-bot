import os

from twitchAPI.twitch import Twitch
import twitchAPI.helper as helper
from discord.ext.commands.core import is_owner
from dotenv import load_dotenv

load_dotenv()

twitch = Twitch(os.getenv("Twitch_Client_ID"), os.getenv("Twitch_Client_Secret"))


def get_user_info(account):
    try:
        user = twitch.search_channels(query=account, first=1)["data"].pop()
        return {"tag": user["broadcaster_login"], "name": user["display_name"]}
    except:
        return None


def get_stream_info(id):
    info = twitch.search_channels(query=id, first=1)["data"].pop()
    
    time = info["started_at"]
    link = f"https://www.twitch.tv/{id}?{time}"
    username = info["display_name"]
    game_name = info["game_name"]
    thumbnail_url = info["thumbnail_url"]
    title = info["title"]

    stream = {
        "link": link,
        "username": username,
        "title": title,
        "game_name": game_name,
        "thumbnail_url": thumbnail_url,
    }
    # TODO stream
    return stream


# if __name__ == "__main__":
# print(get_user_info('bernardo_nevermind_horta'))
# print(get_stream_info("bernardo_nevermind_horta"))
