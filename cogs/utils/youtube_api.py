import configparser
from googleapiclient.discovery import build

configs = configparser.ConfigParser()
configs.read("configs/content_follow.ini")

if configs.get("YOUTUBE", "Available").find("true") == 0:
    api_key = configs.get("YOUTUBE", "Youtube_API_key")
    youtube = build("youtube", "v3", developerKey=api_key)


def channel_by_username(username):
    request = youtube.channels().list(part="snippet", forUsername=username)
    response = request.execute()

    result_count = response["pageInfo"]["totalResults"]
    if result_count == 0:
        return None

    channel = response["items"].pop()
    print(channel)
    channel_id = channel["id"]
    name = channel["snippet"]["title"]

    return {"tag": channel_id, "name": name}


def channel_by_id(channel_id):
    request = youtube.channels().list(part="snippet", id=id)
    response = request.execute()

    result_count = response["pageInfo"]["totalResults"]
    if result_count == 0:
        return None

    channel = response["items"].pop()
    name = channel["snippet"]["title"]

    return {"tag": channel_id, "name": name}


def get_channel_info(channel):
    # if channel is id
    creator = channel_by_id(channel)
    if creator is not None:
        return creator

    # if channel is username
    creator = channel_by_username(channel)
    if creator is not None:
        return creator

    # if nothing found
    return None


def get_latest_video(channel_id):

    # request = youtube.search().list(
    #    part="snippet", channelId=channel_id, maxResults=1, order="date", type="video"
    # )
    # response = request.execute()

    # video = response["items"].pop()

    # username = video["snippet"]["channelTitle"]
    # link = "https://www.youtube.com/watch?v=" + video["id"]["videoId"]

    username = "test"
    link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    post = {"link": link, "username": username}
    return post
