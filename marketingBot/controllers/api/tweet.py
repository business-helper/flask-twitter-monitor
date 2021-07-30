from flask import request, jsonify
from datetime import datetime
import requests
import ast
import uuid
import os, uuid

from marketingBot import app
from marketingBot.config.constants import mPath
from marketingBot.controllers.api import api
from marketingBot.controllers.twitter import create_api
from marketingBot.models.Tweet import db, Tweet
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Media import Media
from marketingBot.controllers.api.api_apps import get_tweepy_instance
from marketingBot.helpers.wrapper import session_required
from marketingBot.helpers.common import json_parse


def get_tweet_embed_info(tweet_id):
  response = requests.get(f"https://publish.twitter.com/oembed?url=https://twitter.com/Interior/status/{tweet_id}")
  return response

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
  embed = get_tweet_embed_info(tweet.entities['id_str']).json()
  if not tweet:
    return jsonify({
      "status": False,
      "message": "Tweet does not exist!",
    })
  return jsonify({
    "status": True,
    "message": "success",
    "data": tweet.to_dict(),
    "embed": embed,
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
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": 'Not found the tweet with ID',
    })
  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  try:
    _tweepy.retweet(tweet.entities['id_str'])
  except Exception as e:
    reason = ast.literal_eval(e.reason)
    print('[Reason]', type(reason), reason[0]['message'])
    return jsonify({
      "status": False,
      "message": reason[0]['message'],
    })
  tweet.updated_at = datetime.utcnow()
  tweet.tweeted = 1
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "You retweeted a tweet!",
  })


@api.route('/tweets/do-tweet/<id>', methods=['POST'])
@session_required
def do_tweet(self, id):
  payload = dict(request.get_json())
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      "status": False,
      "message": 'Not found the tweet with ID',
    })
  # get a tweepy instanace
  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })

  # update tweet record.
  tweet.translated = payload['translated'] if 'translated' in payload else payload.translated
  tweet.updated_at = datetime.utcnow()
  tweet.tweeted = 2
  try:
    _tweepy.update_status(tweet.translated, media_ids = payload['media'] if 'media' in payload else [])
    db.session.commit()
    return jsonify({
      "status": True,
      "message": "You posted a tweet!",
    })
  except Exception as e:
    print('[Tweet Error]', type(e.__dict__['reason']))
    return jsonify({
      'status': False,
      'message': e.__dict__['reason'],
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
  
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      'status': False,
      'message': 'Not found the target tweet!',
    })

  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  tweet.updated_at = datetime.utcnow()
  tweet.tweeted = 3
  db.session.commit()

  try:
    _tweepy.update_status(
      f"@{tweet.entities['user']['screen_name']} {comment_text}",
      media_ids = payload['media'] if 'media' in payload else [],
      in_reply_to_status_id = tweet.entities['id_str'],
    )

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
  
  tweet = Tweet.query.filter_by(id = id).first()
  if not tweet:
    return jsonify({
      'status': False,
      'message': 'Not found the target tweet!',
    })

  _tweepy = get_tweepy_instance()
  if not _tweepy:
    return jsonify({
      "status": False,
      "message": "Cound not create API connection!",
    })
  
  tweet.updated_at = datetime.utcnow()
  tweet.tweeted = 4
  db.session.commit()

  target_tweet_url = f"https://twitter.com/{tweet.entities['user']['screen_name']}/status/{tweet.entities['id_str']}"

  try:
    _tweepy.update_status(
      f"{comment_text} {target_tweet_url}",
      media_ids = payload['media'] if 'media' in payload else [],
    )

    return jsonify({
      "status": True,
      "message": "You quoted to the tweet!",
    })
  except Exception as e:
    print('[Quote Error]', type(e.__dict__))
    return jsonify({
      'status': False,
      'message':'Failed to quote',
    })

