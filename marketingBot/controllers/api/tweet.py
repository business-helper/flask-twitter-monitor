from flask import request, jsonify
from datetime import datetime

from flask.globals import session

from marketingBot.controllers.api import api
from marketingBot.models.Tweet import db, Tweet
from marketingBot.controllers.api.api_apps import get_tweepy_instance
from marketingBot.helpers.wrapper import session_required


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
  return jsonify({
    "status": True,
    "message": "success",
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
  _tweepy.retweet(tweet.entities['id_str'])
  return jsonify({
    "status": True,
    "message": "You retweeted a tweet!",
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
