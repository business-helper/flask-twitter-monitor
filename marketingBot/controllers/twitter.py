import tweepy
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

logger.info(f"Processing tweet id ~")

CONSUMER_KEY = "C8DpNFJYcFTr0MaZjPpSGEyzl"
CONSUMER_SECRET = "tDicaBsTBIu3Oqdk4DmGDkGVpzkfr2UgIJdkqDgQkP8M5O0h4i"
ACCESS_TOKEN = "1052098057922273280-ChPKjuaqHiFLapx3Y26g5EhXUyg7HZ"
ACCESS_TOKEN_SECRET = "71AjifF18MLojnbR7kR8vyNUBHQVvjdL9ZJBLZREA6BL8"

# # Authenticate to Twitter
# auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# # Create API Object
# api = tweepy.API(auth)

def create_api(consumer_key, consumer_secret, access_token, access_token_secret):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth, wait_on_rate_limit=True)
  return api

api = create_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# try:
#   api.update_status("Did you get a vaccine?")
# except Exception as e:
#   print(e)


# user = api.get_user('AdWeek')
# print('User Details:')
# print(user.name)
# print(user.location)
# print(user.status.text)




