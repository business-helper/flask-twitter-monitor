from flask import request, jsonify, send_file
from datetime import datetime
from sqlalchemy.sql import text
import requests
import ast
import uuid
import os, uuid

from marketingBot import app, db
from marketingBot.config.constants import mPath
from marketingBot.controllers.api import api
from marketingBot.controllers.twitter import create_api
from marketingBot.controllers.api.api_apps import get_tweepy_instance
from marketingBot.controllers.task_manager import TweetAction
from marketingBot.models.Tweet import Tweet
from marketingBot.models.Bot import Bot
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Media import Media
from marketingBot.models.Notification import Notification
from marketingBot.helpers.wrapper import session_required
from marketingBot.helpers.common import json_parse, save_as_csv


def get_tweet_embed_info(tweet_id):
  try:
    response = requests.get(f"https://publish.twitter.com/oembed?url=https://twitter.com/Interior/status/{tweet_id}")
    return response
  except Exception as e:
    print(f"[Embend] {tweet_id} error")
    return False

@app.route('/download/csv/<filename>', methods = ['GET'])
@session_required
def download_csv_file_by_name(self, filename):
  file_path = os.path.join(app.root_path, mPath.CSV_PATH, filename)
  return send_file(file_path)

@api.route('/ping-tweet', methods=['GET'])
def api_ping_tweet():
  return jsonify({
    "status": True,
    "message": "Pong from Tweet",
  })


@api.route('/tweets/<id>', methods=['GET'])
@session_required
def get_tweet_by_id(self, id):
  tweet = Tweet.query.filter_by(id=id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": "Tweet does not exist!",
    })
  embed = get_tweet_embed_info(tweet.entities['id_str'])
  if not embed:
    return jsonify({
      'status': False,
      'message': 'It seems the tweet has been deleted!',
    })
  return jsonify({
    "status": True,
    "message": "success",
    "data": tweet.to_dict(),
    "embed": embed.json(),
  })


# ref: https://stackoverflow.com/a/53266167/9644424
@api.route('/tweets/by-id/<id>', methods=['GET'])
# @session_required
def get_tweet_by_status_id(id):
  tweet = db.session.query(Tweet).filter(Tweet.entities['id_str'] == id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": "Not found the tweet",
    })
  return jsonify({
    "status": True,
    "message": "Found it!",
    "data": tweet.to_dict(),
  })

@api.route('/tweets/do-retweet/<id>', methods=['POST'])
@session_required
def do_retweet(self, id):
  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  try:
    tweetAction = TweetAction(instance = _tweepy)
    result = tweetAction.retweet(id)
    if not result:
      return jsonify({
        'status': False,
        'message': 'Failed to retweet',
      })
    return jsonify({
      "status": True,
      "message": "You retweeted a tweet!",
    })
  except Exception as e:
    reason = ast.literal_eval(e.reason)
    print('[Reason]', type(reason), reason[0]['message'])
    return jsonify({
      "status": False,
      "message": reason[0]['message'],
    })


@api.route('/tweets/do-tweet/<id>', methods=['POST'])
@session_required
def do_tweet(self, id):
  payload = dict(request.get_json())
  # update translated text
  tweet = db.session.query(Tweet).filter_by(id = id).first()
  tweet.translated = payload['translated']
  tweet.updated_at = datetime.utcnow()
  db.session.commit()

  bot = db.session.query(Bot).filter_by(id = tweet.bot_id).first()
  if not bot:
    return jsonify({
      "status": False,
      "message": "Bot does not exist for the tweet!",
    })
  session_tweets = Tweet.query.filter_by(session = tweet.session).all()
  rank_indices = list(map(lambda twit: str(twit.rank_index), session_tweets))
  db.session.commit()
  # get a tweepy instanace
  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  tweetAction = TweetAction(instance = _tweepy, bot_object = bot.to_dict(), ranks = rank_indices)
  try:
    result = tweetAction.tweet(id, media = payload['media'] if 'media' in payload else [])
    if not result:
      return jsonify({'status': False, 'message': 'Failed to tweet...'})
    return jsonify({
      "status": True,
      "message": "You posted a tweet!",
    })
  except Exception as e:
    print('[Tweet Error]', type(e.__dict__['reason']))
    return jsonify({
      'status': False,
      'message': str(e),
    })


@api.route('/tweets/translate/<id>', methods=['PUT'])
@session_required
def save_tweet_translation(self, id):
  payload = dict(request.get_json())
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": "Not found the tweet with ID!",
    })
  tweet.translated = payload['translated']
  tweet.updated_at = datetime.utcnow()
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "success",
  })


@api.route('/tweets/<id>', methods=['DELETE'])
@session_required
def delete_tweet_by_id(self, id):
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": "Tweet does not exist!",
    })
  db.session.delete(tweet)
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "A tweet has been deleted!",
  })


@api.route('/tweets/embed-info/<id>', methods = ['GET'])
def get_tweet_embed_info_req(id):
  response = get_tweet_embed_info(id).json()
  print(type(response), response)
  return jsonify(response)


@api.route('/tweets/upload/media', methods=['POST'])
@session_required
def upload_media(self):
  print('[S][Upload Media]')
  payload = dict(request.form)

  file_keys = list(request.files.keys())
  if len(file_keys) == 0:
    return jsonify({
      "status": True,
      "message": "No files selected!",
      "title": "Upload Media to Twitter",
      "data": [],
    })

  # create an instance of API v1
  api_key = AppKey.query.filter_by(user_id = self.id).first()
  api_instance = create_api(
    consumer_key=api_key.consumer_key,
    consumer_secret=api_key.consumer_secret,
    access_token=api_key.access_token,
    access_token_secret=api_key.access_token_secret,    
  )

  if not api_key:
    return jsonify({
      "status": False,
      "message": "Not found the valid API key!",
      "title": "Upload Media to Twitter",
      "data": [],
    })

  media_ids = []

  for file_key in file_keys:
    file_ = request.files[file_key]
    file_extension = os.path.splitext(file_.filename)

    # to-do: check file extension if it's image.

    str_uuid = str(uuid.uuid4())
    new_filename = f"{str_uuid}{file_extension}"
    rel_path = os.path.join(mPath.MEDIA_PATH, new_filename)
    dest_path = os.path.join(app.root_path, rel_path)
    file_.save(dest_path)
    # upload to twitter
    media_t = api_instance.media_upload(filename = new_filename, file = file_, media_category = 'tweet_image')
    print('Media Uploaded', media_t)
    # create media in db.
    media_db = Media(
      user_id = self.id,
      origin_name = file_.filename,
      path = rel_path,
      media_id = media_t.media_id_string,
    )
    db.session.add(media_db)
    db.session.commit()

    media_ids.append(media_t.media_id_string)
  
  return jsonify({
    "status": True,
    "message": "Media uploaded successfully!",
    "title": "Upload Media to Twitter",
    "data": media_ids,
  })


@api.route('/tweets/comment/<id>', methods=['POST'])
@session_required
def comment_to_tweet(self, id):
  payload = dict(request.get_json())
  comment_text = payload['comment']
  # update translated text
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      'status': False,
      'message': 'Not found the target tweet!',
    })
  # tweet.translated = comment_text
  # tweet.updated_at = datetime.utcnow()
  db.session.commit()

  bot = Bot.query.filter_by(id = tweet.bot_id).first()
  session_tweets = Tweet.query.filter_by(session = tweet.session).all()
  rank_indices = list(map(lambda twit: str(twit.rank_index), session_tweets))
  db.session.commit()


  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })

  try:
    tweetAction = TweetAction(instance = _tweepy, bot_object = bot.to_dict(), ranks = rank_indices)
    result = tweetAction.comment(
      id = id,
      comment = comment_text,
      media = payload['media'] if 'media' in payload else [],
    )
    if not result:
      return jsonify({
        'status': False,
        'message': 'Failed to comment',
      })
    return jsonify({
      "status": True,
      "message": "You commented to the tweet!",
    })
  except Exception as e:
    print('[Comment Error]', type(e.__dict__))
    return jsonify({
      'status': False,
      'message':'Failed to comment',
    })


@api.route('/tweets/quote/<id>', methods=['POST'])
@session_required
def comment_with_quote(self, id):
  payload = dict(request.get_json())
  comment_text = payload['text']
  # update translated text
  tweet = Tweet.query.filter_by(id = id).first()
  # tweet.translated = comment_text
  # tweet.updated_at = datetime.utcnow()
  # db.session.commit()

  bot = Bot.query.filter_by(id = tweet.bot_id).first()
  session_tweets = Tweet.query.filter_by(session = tweet.session).all()
  rank_indices = list(map(lambda twit: str(twit.rank_index), session_tweets))
  db.session.commit()


  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  try:
    tweetAction = TweetAction(instance = _tweepy, bot_object = bot.to_dict(), ranks = rank_indices)
    result = tweetAction.quote(
      id = id,
      comment = comment_text,
      media = payload['media'] if 'media' in payload else [],
    )
    if not result:
      return jsonify({
        'status': False,
        'message': 'Failed to quote!',
      })
    return jsonify({
      "status": True,
      "message": "You quoted to the tweet!",
    })
  except Exception as e:
    print('[Quote Error]', type(e.__dict__), e)
    return jsonify({
      'status': False,
      'message':'Failed to quote',
    })

@api.route('/tweets/download', methods=['POST'])
@session_required
def download_tweets(self):
  try:
    user_id = self.id
    payload = dict(request.get_json())
    fields = payload['fields']
    filter = payload['filter']

    tweets = db.session.query(
        Tweet
      ).join(Bot, Bot.id == Tweet.bot_id, isouter = True
      ).join(Notification, Notification.id == Tweet.session, isouter = True
      ).filter(Tweet.user_id == user_id)
    if 'keyworkd' in filter and filter['keyword']:
      tweets = tweets.filter(Tweet.text.like(f"%{filter['keyword']}%"))
    if 'bot' in filter and int(filter['bot']) > 0:
      tweets = tweets.filter(Tweet.bot_id == filter['bot'])
    if 'session' in filter and int(filter['session']) > 0:
      tweets = tweets.filter(Tweet.session == filter['session'])
    tweets =  tweets.with_entities(Tweet.id, Tweet.bot_id, Tweet.target, Tweet.text, Tweet.translated, Tweet.tweeted, Tweet.entities, Tweet.created_at, Tweet.metrics, Tweet.rank_index, Bot.name.label('bot_name'), Notification.created_at.label('session_time')
      ).all()

    header_map = {
      "bot": 'Bot',
      "session": 'Session',
      "target": 'Target',
      "text": 'Text',
      "translated": 'Translated',
      "followers": 'Followers',
      "friends": 'friends',
      "statuses": 'Total Tweets',
      "lists": 'Lists',
      "retweets": 'Retweets',
      "likes": 'Likes',
      "rank": 'Rank Index',
      "tweeted": 'Tweeted',
      "time": 'Time,'
    }
    headers = list(map(lambda key: header_map[key], fields))
    print('[Download][Header]', type(headers), headers)
    object_array = []
    for tweet in tweets:
      print('[Tweet]', type(tweet))
      object_array.append(tweet_csv_row_data(dict(tweet), fields))
    file_name = save_as_csv(headers, object_array, self.id)
    return jsonify({
      "status": True,
      "message": 'success',
      "file": file_name,
    })
  except Exception as e:
    print(f"[Download CSV][Error] {str(e)}")
    # raise e
    return jsonify({
      "status": False,
      "message": "Something weng wrong!",
      "details": str(e),
    })


def tweet_csv_row_data(tweet, fields):
  data = []
  tweet_actions = ['None', 'Retweeted', 'Tweeted', 'Commentted', 'Quoted']
  for key in fields:
    if key == 'bot':
      data.append(tweet['bot_name'])
    elif key == 'session':
      data.append(tweet['session_time'])
    elif key == 'target':
      data.append(tweet['target'])
    elif key == 'text':
      data.append(f"\"{tweet['text']}\"")
    elif key == 'translated':
      data.append(f"\"{tweet['translated']}\"")
    elif key == 'followers':
      data.append(tweet['metrics']['followers'] if 'followers' in tweet['metrics'] else 0)
    elif key == 'friends':
      data.append(tweet['metrics']['friends'] if 'friends' in tweet['metrics'] else 0)
    elif key == 'statuses':
      data.append(tweet['metrics']['statuses'] if 'statuses' in tweet['metrics'] else 0)
    elif key == 'lists':
      data.append(tweet['metrics']['listed'] if 'listed' in tweet['metrics'] else 0)
    elif key == 'retweets':
      data.append(tweet['metrics']['tweet']['retweets'] if 'tweet' in tweet['metrics'] else 0)
    elif key == 'likes':
      data.append(tweet['metrics']['tweet']['favorite'] if 'tweet' in tweet['metrics'] else 0)
    elif key == 'rank':
      data.append(str(tweet['rank_index']))
    elif key == 'tweeted':
      data.append(tweet_actions[int(tweet['tweeted'])])
    elif key == 'time':
      data.append(tweet['created_at'])
  return data
