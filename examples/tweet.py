"""
In this file im going to show you a quick example to how you can tweet a message to twitter.
"""
import pytweet

client = pytweet.Client(
    "Your Bearer Token Here!!!",
    consumer_key="Your consumer_key here",
    consumer_secret="Your consumer_secret here",
    access_token="Your access_token here",
    access_token_secret="Your access_token_secret here",
)  # if you dont have one make an application in https://apps.twitter.com

client.tweet("just setting up my twttr bot using #PyTweet")
# You could also mention a user using @Username, put hashtags using #Hashtags and url thats going to be embedded to your tweet.