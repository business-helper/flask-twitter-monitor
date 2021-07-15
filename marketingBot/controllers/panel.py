from flask import Flask, render_template, jsonify, redirect, url_for, escape, request
from sqlalchemy.sql import text
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask import flash

from marketingBot import app
from marketingBot.models.AppKey import db, AppKey
from marketingBot.models.Bot import Bot
from marketingBot.models.Notification import Notification
from marketingBot.models.Tweet import Tweet
from marketingBot.helpers.common import unset_login_session, validate_session, timestamp
from marketingBot.helpers.wrapper import session_required

@app.context_processor
def my_utility_processor():
  def time_now():
    return timestamp()
  def current_route():
    return request.url_rule.rule
  
  return dict(timestamp=time_now, current_route = current_route)

@app.route('/ping')
def ping():
  print('[Ping] requested')
  return jsonify({ "status": True, "message": "Pong" })

@app.route('/dashboard', methods=['GET'])
@session_required
def dashboard(self):
  return render_template('panel/dashboard.html')

@app.route('/api-apps')
@session_required
def api_apps(self):
  return render_template('panel/api-apps.html')


@app.route('/load-api-apps')
@session_required
def load_api_apps(self):
  skip = request.args.get('start')
  limit = request.args.get('length')
  sortCol = request.args.get('order[0][column]')
  sortDir = request.args.get('order[0][dir]')
  user_id = self.id
  keyword = request.args.get('search[value]')

  apps = AppKey.query.filter_by(user_id=user_id).limit(limit).offset(skip)
  
  data = []
  for idx, app in enumerate(apps):
    data.append([idx + 1, app.name, f"{app.consumer_key}:{app.consumer_secret}:{app.access_token}:{app.access_token_secret}:{app.bearer_token}", app.valid, app.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': 10,
    'iTotalDisplayRecords':10,
  })


# Add a new API app.
@app.route('/api-app', methods=['POST'])
@session_required
def add_api_app(self):
  payload = request.get_json()
  print('[Payload]', payload)
  isExist = AppKey.query.filter_by(consumer_key=payload['consumer_key'], consumer_secret=payload['consumer_secret']).first()
  if (isExist):
    # flash('This API app already exists!')
    # return render_template('panel/api-apps.html')
    return jsonify({
      "status": False,
      "message": "This API app already exists!",
    })
  print('[Active]', payload['valid'])
  appKey = AppKey(
    user_id = self.id,
    consumer_key = payload['consumer_key'],
    consumer_secret = payload['consumer_secret'],
    access_token = payload['access_token'],
    access_token_secret = payload['access_token_secret'],
    bearer_token = payload['bearer_token'],
    name = payload['name'],
    valid = payload['valid'],
  )
  db.session.add(appKey)
  db.session.commit()
  # return render_template('panel/api-apps.html')
  return jsonify({
    "status": True,
    "message": "Data has been added!",
  })


@app.route('/bots', methods=['GET'])
@session_required
def bots_page(self):
  api_keys = AppKey.query.filter_by(user_id=self.id,valid=True).all()
  apps = []
  for api_key in api_keys:
    apps.append(api_key.to_dict())
  data = {
    "time": timestamp(),
    "api_apps": apps,
    "names": ['A', 'B']
  }
  return render_template('panel/bots.html', data=data)


@app.route('/load-bots', methods=['GET', 'POST'])
@session_required
def load_bots_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  user_id = self.id

  columns = ['bots.id', 'name', 'type', 'targets', '', 'api_keys', '', '', 'status']
  order_by = text(f"{columns[int(sortCol)]} {sortDir}")

  print('[Sort]', sortCol, sortDir)
  bots = Bot.query.filter_by(user_id=user_id).order_by(order_by).limit(limit).offset(skip)
  total = Bot.query.filter_by(user_id = user_id).count()
  app_keys = AppKey.query.filter_by(user_id=user_id).all()
  dict_keys = {}

  for app_key in app_keys:
    dict_keys[str(app_key.id)] = app_key.to_dict()

  data = []
  for idx, bot in enumerate(bots):
    bot = bot.format()
    bot_keys = []
    for key in bot.api_keys:
      key = str(key)
      if key in dict_keys:
        bot_keys.append(dict_keys[key])

    data.append([idx + 1, bot.name, bot.type, bot.targets, [float(bot.period), bot.start_time, bot.end_time], bot_keys, bot.inclusion_keywords, bot.exclusion_keywords, bot.status, bot.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })


# 
# Tweet Page
@app.route('/tweets', methods=['GET'])
@session_required
def tweets_page(self):
  return render_template('panel/tweets.html')

@app.route('/load-tweets', methods=['GET', 'POST'])
@session_required
def load_tweets_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  columns = ['tweets.id', 'bot_name', 'target', 'text', 'translated',
    "JSON_EXTRACT(tweets.metrics, '$.followers')",
    "JSON_EXTRACT(tweets.metrics, '$.friends')",
    "JSON_EXTRACT(tweets.metrics, '$.statuses')",
    "JSON_EXTRACT(tweets.metrics, '$.listed')",
    "JSON_EXTRACT(tweets.metrics, '$.tweet.retweets')",
    "JSON_EXTRACT(tweets.metrics, '$.tweet.favorite')",
    'tweeted', 'tweets.created_at']

  user_id = self.id
  # keyword = request.args.get('search[value]')
  # tweets = Tweet.query.filter_by(user_id = user_id).limit(limit).offset(skip)
  order_by = text(f"{columns[int(sortCol)]} {sortDir}")
  tweets = db.session.query(
      Tweet, Bot
    ).filter(Tweet.bot_id == Bot.id
    ).filter(Tweet.user_id == user_id
    ).with_entities(Tweet.id, Tweet.bot_id, Tweet.target, Tweet.text, Tweet.translated, Tweet.tweeted, Tweet.entities, Tweet.created_at, Tweet.metrics, Bot.name.label('bot_name')
    ).order_by(order_by).limit(limit).offset(skip)

  # total = Tweet.query.filter_by(user_id = user_id).count()
  total = db.session.query(Tweet, Bot).filter(Bot.id == Tweet.bot_id).count()

  bots = Bot.query.filter_by(user_id = user_id).all()
  dict_bots = {}
  for bot in bots:
    dict_bots[str(bot.id)] = bot.to_dict()
  
  data = []
  for idx, tweet in enumerate(tweets):
    data.append([
      idx + 1,
      tweet.bot_name,
      tweet.target,
      tweet.text,
      tweet.translated,
      tweet.metrics['followers'] if 'followers' in tweet.metrics else 0,
      tweet.metrics['friends'] if 'friends' in tweet.metrics else 0,
      tweet.metrics['statuses'] if 'statuses' in tweet.metrics else 0,
      tweet.metrics['listed'] if 'listed' in tweet.metrics else 0,
      tweet.metrics['tweet']['retweets'] if 'tweet' in tweet.metrics else 0,
      tweet.metrics['tweet']['favorite'] if 'tweet' in tweet.metrics else 0,
      tweet.tweeted,
      tweet.created_at,
      { "id": tweet.id, "tweet_id": tweet.entities['id_str'] },
    ])
  return jsonify({
    'data': data,
    'draw': payload['draw'],
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })

#
# Notification Page
@app.route('/notifications', methods=['GET'])
@session_required
def notification_page(self):
  return render_template('panel/notifications.html')


@app.route('/load-notifications', methods=['GET', 'POST'])
@session_required
def load_notifications_root(self):
  payload = request.form #dict(request.get_json())
  skip = payload['start']
  limit = payload['length']
  sortCol = payload['order[0][column]']
  sortDir = payload['order[0][dir]']
  columns = ['notifications.id', 'bot_name', 'notifications.text',
    "JSON_EXTRACT(notifications.payload, '$.type')",
    'notifications.created_at']

  user_id = self.id

  order_by = text(f"{columns[int(sortCol)]} {sortDir}")
  notifications = db.session.query(
      Bot, Notification
    ).filter(Bot.id == Notification.bot_id
    ).filter(Notification.user_id == user_id
    ).with_entities(Notification.id, Notification.user_id, Notification.bot_id, Notification.text, Notification.payload, Notification.created_at, Bot.name.label('bot_name')
    ).order_by(order_by).limit(limit).offset(skip)

  # total = Notification.query.filter_by(user_id = user_id).count()
  total = db.session.query(Bot, Notification).filter(Bot.id == Notification.bot_id).count()

  data = []
  for idx, notification in enumerate(notifications):
    data.append([
      idx + 1,
      notification.bot_name,
      notification.text,
      notification.payload,
      notification.created_at,
      { "id": notification.id },
    ])
  return jsonify({
    'data': data,
    'draw': payload['draw'],
    'iTotalRecords': total,
    'iTotalDisplayRecords': total,
  })
