import os
from dotenv import load_dotenv
import twitter

import json

load_dotenv()


twitter_api = twitter.Api(
    consumer_key=os.getenv("Twitter_API_key"),
    consumer_secret=os.getenv("Twitter_API_secret"),
    access_token_key=os.getenv("Twitter_Access_token_key"),
    access_token_secret=os.getenv("Twitter_Access_token_secret"),
)


def get_tweets(api=twitter_api, screen_name=None):
    timeline = api.GetUserTimeline(screen_name=screen_name, count=10)
    earliest_tweet = min(timeline, key=lambda x: x.id).id
    print("getting tweets before:", earliest_tweet)

    while True:
        tweets = api.GetUserTimeline(
            screen_name=screen_name, max_id=earliest_tweet, count=10
        )
        new_earliest = min(tweets, key=lambda x: x.id).id

        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting tweets before:", earliest_tweet)
            timeline += tweets

    return timeline


def get_tweet(api=twitter_api, screen_name=None):
    user = twitter_api.GetUser(screen_name=screen_name)
    link = f"https://twitter.com/{user.screen_name}/status/{user.status.id}"
    return link


# except:
#    return print (f"error invalid twitter user: {screen_name}")


def user_is_valid(screen_name):
    try:
        twitter_api.GetUser(screen_name=screen_name)
        return True
    except:
        return False
