import configparser
import tweepy

configs = configparser.ConfigParser()
configs.read("configs/content_follow.ini")

if configs.get('TWITTER', 'Available').find('true') == 0:

    auth = tweepy.OAuthHandler(
        consumer_key=configs.get('TWITTER', 'Twitter_API_key'),
        consumer_secret=configs.get('TWITTER', 'Twitter_API_secret'),
    )
    auth.set_access_token(
        key=configs.get('TWITTER', 'Twitter_Access_token_key'),
        secret=configs.get('TWITTER', 'Twitter_Access_token_secret'),
    )

    api = tweepy.API(auth)


def get_user_info(account):
    try:
        user = api.get_user(screen_name=account)
        return {"tag": user.id_str, "name": user.screen_name}
    except:
        return None


def get_latest_tweet(id):
    user = api.get_user(user_id=id)

    username = user.name
    link = f"https://twitter.com/{user.screen_name}/status/{user.status.id}"

    post = {"link": link, "username": username}
    return post
