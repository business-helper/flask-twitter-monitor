from flask import request, jsonify
from datetime import datetime
import requests
import ast

from marketingBot.controllers.api import api
from marketingBot.models.Tweet import db, Tweet
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
  _tweepy.update_status(tweet.translated, media_ids = [])
  db.session.commit()
  return jsonify({
    "status": True,
    "message": "You posted a tweet!",
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
