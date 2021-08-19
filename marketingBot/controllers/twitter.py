from flask import request, jsonify
import tweepy
from pytwitter import Api
import shutil, os
import logging
from dotenv import load_dotenv

from marketingBot import app

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

logger.info(f"Processing tweet id ~")

CONSUMER_KEY = "rTyqeH43KVVA96eRHXJxnzMOS"
CONSUMER_SECRET = "oQLAlEXs3DipiN8ow1kmrtggOahba9zyZuWF691Bm1kDgEFt7E"
ACCESS_TOKEN = "1052098057922273280-JTBl0wNmvkcRvzXVUUkJHKvDQ5ae6Z"
ACCESS_TOKEN_SECRET = "eqhupIfMr7uvklYHSHtu7IVvptlQrYY6tTN8YJxUps1IK"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABgWEAEAAAAA8b6PoxoYNew%2BE4nnS7has9CofwA%3D9shXMqslVNrJecsYmW9iEuIvNi0rhNRLN73WGp9bQiEd9LmDRj"

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

def create_api_v12(consumer_key, consumer_secret, access_token, access_token_secret):
  client = tweepy.Client(bearer_token=BEARER_TOKEN,
    consumer_key = consumer_key
    , consumer_secret = consumer_secret
    , access_token = access_token
    , access_token_secret = access_token_secret)
  return client

def create_api_v2(bearer_token):
  api = Api(
    bearer_token = bearer_token
    # consumer_key = consumer_key,
    # consumer_secret = consumer_secret,
    # access_token = access_token,
    # access_token_secret = access_token_secret,
  )
  return api

# api = create_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

print('[App path]', app.root_path, app.instance_path)

# file upload
@app.route('/file-upload-test', methods=['POST'])
def file_upload_test():
  # file = request.files.get('file').read().decode('utf-8') if 'targets' in request.files
  file = request.files['file']
  print('[Files]', file, file.filename, list(request.files.keys()))

  dest = os.path.join(app.root_path, 'assets/uploads/media', 'test.png')
  file.save(dest)
  print('[Dest]', dest)
  # shutil.copy(file, dest)
  # print('[Before Upload]', api, file.name)
  # print('[Update API]', type(api.media_upload))
  # response = api.media_upload(filename = request.files.get('file').name, file = file, media_category = 'tweet_image')
  # print('[Upload Result]', response)
  return jsonify({
    "status": True,
    "message": "uploaded?"
  })


# user_timeline = api.user_timeline(screen_name='CMIContent')

# try:
#   api.update_status("Did you get a vaccine?")
# except Exception as e:
#   print(e)


# user = api.get_user('AdWeek')
# print('User Details:')
# print(user.name)
# print(user.location)
# print(user.status.text)
# print('[User] ID', user.id)
# statuses = api.lookup_users([user.id])
# print('[Statuses]', statuses[0].status)

## ----------- V1
# api_v1 = create_api(
#   consumer_key = CONSUMER_KEY,
#   consumer_secret = CONSUMER_SECRET,
#   access_token = ACCESS_TOKEN,
#   access_token_secret = ACCESS_TOKEN_SECRET,
#   )

# status = api_v1.get_status('1410639112613163009', tweet_mode = 'extended')
# statuses = api_v1.statuses_lookup(id_=['1410639112613163009'], tweet_mode = 'extended')
# status = statuses[0]

# print('[V1][Status]', status.retweeted_status.full_text)

# user_v1 = api_v1.get_user(screen_name = 'BusiHelper')
# print('[User] V1:', user_v1)


## ----------- V2
# api_v2 = create_api_v2(bearer_token = BEARER_TOKEN)
# user_v2 = api_v2.get_user(username = 'Adweek')

# print('[User] V2:', user_v2.__dict__['data'].id)

# timelines = api_v2.get_timelines(user_id = user_v2.__dict__['data'].id, start_time="2021-07-01T00:00:00Z", end_time="2021-07-05T00:00:00Z",
#   media_fields = ['url', 'public_metrics' ],
#   expansions=['author_id', 'referenced_tweets.id', 'referenced_tweets.id.author_id'],
#   tweet_fields = ['author_id', 'entities', 'id', 'lang', 'public_metrics', 'text', 'referenced_tweets'],
#   user_fields = ['id', 'name', 'public_metrics', 'verified']
# )
# _twit = timelines.data[0].__dict__
# print('[Timeline] V2', timelines.data[0].__dict__)
# print('[Text] V2', timelines.data[0].__dict__['text'])
# print('[Entities]', timelines.data[0].__dict__['entities'].__dict__)
# print('[Public Metrics]', timelines.data[0].__dict__['public_metrics'].__dict__)
# print('[Reference Tweet]', _twit['referenced_tweets'][0].__dict__)



# api_v2 = create_api_v2(consumer_key = CONSUMER_KEY, 
#   consumer_secret = CONSUMER_SECRET, access_token = ACCESS_TOKEN, access_token_secret = ACCESS_TOKEN_SECRET)
# user1 = api_v2.get_user(username = 'BusiHelper')
# print('[API V2][User]', user1)
