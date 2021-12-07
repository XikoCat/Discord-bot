import configparser
from twitchAPI.twitch import Twitch

configs = configparser.ConfigParser()
configs.read("configs/content_follow.ini")

if configs.get('TWITCH', 'Available').find('true') == 0:
    twitch = Twitch(configs.get('TWITCH', 'Twitch_Client_ID'), configs.get('TWITCH', 'Twitch_Client_Secret'))


def get_user_info(account):
    try:
        user = twitch.search_channels(query=account, first=1)["data"].pop()
        return {"tag": user["broadcaster_login"], "name": user["display_name"]}
    except:
        return None


def get_stream_info(id):
    info = twitch.search_channels(query=id, first=1)["data"]
    if len(info) == 0:
        print(f"Error getting twitch info for {id}")
        return None

    info = info.pop()

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
