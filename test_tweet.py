import os

import tweepy

api_key = os.environ["API_KEY"]
api_secret = os.environ["API_SECRET_KEY"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

# auth = tweepy.OAuthHandler(api_key, api_secret)
# auth.set_access_token(access_token, access_token_secret)
# api = tweepy.API(auth)

message = 'ツイートテスト'
# api.update_status(status = message,)

client = tweepy.Client(
    consumer_key        = api_key,
    consumer_secret     = api_secret,
    access_token        = access_token,
    access_token_secret = access_token_secret,
)

client.create_tweet(text = message)