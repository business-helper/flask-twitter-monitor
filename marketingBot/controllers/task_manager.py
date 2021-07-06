from datetime import datetime
from flask import jsonify, request
import threading
import time
import tweepy
from pytwitter import Api
# from uwsgidecorators import *

from marketingBot import app
from marketingBot.config.constants import socket_event
from marketingBot.controllers.socket import io_notify_user
from marketingBot.models.Bot import db, Bot
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Tweet import Tweet
from marketingBot.helpers.common import translate

botThreads = {}

@app.before_first_request
def initialize_bots():
  print(f"[Tasks] initializing statuses...")
  Bot.query.update({ Bot.status: 'IDLE' });
  db.session.commit()


initialize_bots()

class BotDemo:
  name = None
  interval = 5

  def __init__(self, name, interval):
    self.name = name
    self.interval = interval



class BotThread(threading.Thread):
  thread = None
  stopped = True
  _iterN = 0

  name = ''
  _interval = 5
  bot = None
  apis = []
  apis_v2 = []
  targets = {}
  last_tweet_ids = {}
  one_time_batch = 50

  def __init__(self, bot, **args):
    threading.Thread.__init__(self)
    self.name = bot.name
    self._interval = bot.period
    self.bot = bot.to_dict()
    # self.event = threading.Event()
    self.stopped = True
    for screen_name in self.bot['targets']:
      self.last_tweet_ids[screen_name.strip()] = {
        "now": None,
        "prev": None,
      }
    # self.apis = self.apis_v2 = self.targets = self.last_tweet_ids = []
    
  def start(self):
    print(f"[Task] starting '{self.name}'")
    self.stopped = False
    self.create_apis()
    if len(self.apis) == 0:
      return False
    # self.validate_targets()
    #if there is not api, then no need to proceed.
    if self.bot['type'] == 'REAL_TIME':
      self.execute_loop()
    elif self.bot['type'] == 'ONE_TIME':
      self.create_v2_apis()
      self.start_one_time_batch()


  def stop(self):
    print(f"[Task] stopping '{self.name}'")
    self.stopped = True

  # @postfork
  def create_apis(self):
    print('[API Keys]', self.bot['api_keys'], type(self.bot['api_keys']))
    if len(self.bot['api_keys']) > 0:
      for api_key_id in self.bot['api_keys']:
        api_key = AppKey.query.filter_by(id=api_key_id).first()

        api_instance = self.create_tweepy_instance(api_key.consumer_key, api_key.consumer_secret, api_key.access_token, api_key.access_token_secret)
        if not api_instance:
          return print('[API Instance] Failed to create.', api_key_id)
        self.apis.append(api_instance)
    
  def create_v2_apis(self):
    if len(self.bot['api_keys']) > 0:
      for api_key_id in self.bot['api_keys']:
        api_key = AppKey.query.filter_by(id=api_key_id).first()
        if not api_key.bearer_token:
          continue
        try:
          inst = Api(bearer_token = api_key.bearer_token)
          self.apis_v2.append(inst)
        except Exception as e:
          print(f"[Bot][{self.bot['name']}][API V2] failed to create... {api_key_id}")



  def validate_targets(self):
    if len(self.apis) == 0:
      return []
    for user_id in self.bot['targets']:
      user_id = user_id.strip()
      try:
        user = self.apis[0].get_user(user_id)
        # self.targets.append(user.id)
        self.targets[str(user_id)] = user.id_str
      except Exception as e:
        pass
    print('[Targets]', type(self.bot['targets']), self.bot['targets'], self.targets)

  def execute_loop(self):
    def func_wrapper():
      if self.stopped:
        return False
      self.execute_loop()
      self.processor()
    t = threading.Timer(self._interval * len(self.apis), func_wrapper)
    t.start()

  def start_one_time_batch(self):
    if len(self.apis_v2) > 0:
      api_inst = self.apis_v2[0]
      for screen_name in self.bot['targets']:
        self.analyze_target(screen_name = screen_name, api_inst = api_inst)
    else:
      print(f"[Bot][{self.bot['name']}]No available API v2 instances")


  def processor(self):
    print(f"[Processing] {self.name} {str(self._iterN)}")
    self.monitor_accounts()


  def create_tweepy_instance(self, consumer_key, consumer_secret, access_token, access_token_secret):
    try:
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.set_access_token(access_token, access_token_secret)
      api = tweepy.API(auth, wait_on_rate_limit=True)
      # test one more to check if the credentials are valid.
      api.me()
      return api
    except Exception as e:
      print(f"[TweepyInstance] {str(e)}")
      return False

  def monitor_accounts(self):
    print(f"[MonitorAccount]', Interval: {self._interval}s, APIs: {len(self.apis)}")

    for idx, api in enumerate(self.apis):

      # if idx > 0:
      #   time.sleep(self._interval)
      if len(self.bot['targets']) > 0:
        try:
          # users = api.lookup_users(list(self.targets.values()), include_entities=True, tweet_mode="extended")
          users = api.lookup_users(screen_names=self.bot['targets'], include_entities=True, tweet_mode="extended")
          # print('[LookUp] Statuses ', users[0].status)
          print(f"[MonitorResult] {len(users)} targets, IDs: {list(map(lambda user:user.status.id, users))}")
          for user in users:
            self.process_monitor_result(user, api)
          self._iterN += 1
        except Exception as e:
          print('[LookUp] Error ', str(e))
          return False

  def process_monitor_result(self, user, api):
    screen_name = user.screen_name
    tweet_id = user.status.id_str

    self.last_tweet_ids[screen_name] = {
      "prev": self.last_tweet_ids[screen_name]['now'],
      "now": tweet_id,
    }
    # print('[Status]', user.status)
    metrics = {
      "verified": user.verified,
      "followers": user.followers_count,
      "friends": user.friends_count,
      "listed": user.listed_count,
      "favorites": user.favourites_count,
      "statuses": user.statuses_count,
      "tweet": {
        # "retweeted": user.status.retweeted_status,
        # "quotes": user.status.quote_count,
        # "replies": user.status.reply_count,
        "retweets": user.status.retweet_count,
        "favorite": user.status.favorite_count,
        "retweeted_by_me": user.status.retweeted,
        "lang": user.status.lang,
      },
    }
    # print('[Metrics]', type(user), metrics)

    is_new_tweet = self.last_tweet_ids[screen_name]['now'] != self.last_tweet_ids[screen_name]['prev'] #(self._iterN > 0 and self.last_tweet_ids[screen_name] and tweet_id != self.last_tweet_ids[screen_name]) or self._iterN == 0

    # update last tweet id
    # self.last_tweet_ids[screen_name] = tweet_id

    metric_matches = self.satisfy_metrics(metrics)

    if is_new_tweet and metric_matches:
      print(f"[NEW_TWEET_FOUND]", self.last_tweet_ids, tweet_id, self._iterN)
      # tweet = self.apis[0].get_status(tweet_id, tweet_mode = 'extended')
      self.postprocess_new_tweet(user.status._json, screen_name, metrics)

  def analyze_target(self, screen_name, api_inst):
    ## analysis data
    tweets = {
      "total": 0,
      "filtered": 0,
    }

    api_v1 = self.apis[0]
    print('[Screen Name]', screen_name)
    target_info = api_inst.get_user(username = screen_name, user_fields=['public_metrics'])

    # api_v2 = create_api_v2(bearer_token = BEARER_TOKEN)
    # user_v2 = api_v2.get_user(username = 'Adweek')

    target_metrics = target_info.data.public_metrics.__dict__
    # print('[Target Info]', target_info, target_info.data)
    target_id = target_info.data.id
    print('[Target Id]', target_id)
    start_time = self.format_time_v2(self.bot['start_time'])
    end_time = self.format_time_v2(self.bot['end_time'])
    # since_id = None #"1408485784840065028"
    try:
      while(True):
        # if start time is later than end time, then break;
        if start_time > end_time:
          break;
        timelines = api_inst.get_timelines(
          user_id = target_id,
          start_time=start_time,
          end_time=end_time,
          # since_id = since_id,
          max_results = self.one_time_batch,
          media_fields = ['url', 'public_metrics' ],
          expansions=['author_id', 'referenced_tweets.id', 'referenced_tweets.id.author_id'],
          tweet_fields = ['author_id', 'entities', 'id', 'lang', 'public_metrics', 'text', 'created_at', 'referenced_tweets'],
          user_fields = ['id', 'name', 'public_metrics', 'verified']
        )
        # print('[timelines]', timelines)
        print('[End Time] Old: ', end_time)
        end_time = timelines.data[len(timelines.data) - 1].created_at
        print('[End Time] New: ', end_time)

        ## analysis
        tweets['total'] += len(timelines.data)

        ## check the metrics match first
        filtered_tweets = {}
        for tweet in timelines.data:
          # print('[Tweet]', tweet.created_at)
          # print('[public metrics]', tweet.id, tweet.public_metrics.__dict__)

          tweet_id = tweet.id
          metrics = {
            "verified": target_info.data.verified,
            "followers": target_metrics['followers_count'],
            "friends": target_metrics['following_count'],
            "listed": target_metrics['listed_count'],
            "favorites": target_metrics['favorite_count'] if 'favorite_count' in target_metrics else None,
            "statuses": target_metrics['tweet_count'],
            "tweet": {
              "retweets": tweet.public_metrics.retweet_count,
              "favorite": tweet.public_metrics.like_count,
              "quotes": tweet.public_metrics.quote_count,
              "retweeted_by_me": False,
              "lang": tweet.lang,
            },
          }
          # print('[Metrics]', metrics)
          if self.satisfy_metrics(metrics):
            filtered_tweets[tweet_id] = { "metrics": metrics }
        filtered_tweet_ids = list(filtered_tweets.keys())
        if len(filtered_tweet_ids) == 0:
          break;

        ## get tweets and check keyword match
        print('[Filtered]', filtered_tweet_ids)
        full_tweets = api_v1.statuses_lookup(id_=filtered_tweet_ids, tweet_mode = 'extended')
        # print('[Full Tweets]', full_tweets)
        for full_tweet in full_tweets:
          full_text = self.parse_full_text(full_tweet)
          # filtered_tweets[full_tweet.id_str]['full_text'] = full_text
          # filtered_tweets[full_tweet.id_str]['keyword_match'] = self.matches_keywords(full_text)
          # filtered_tweets[full_tweet.id_star] = {
          #   "full_text": full_text,
          #   "keyword_matched": self.matches_keywords(full_text),
          #   "entities": full_text._json,
          # }
          translated = translate(src_text=full_text)

          if self.matches_keywords(full_text):
            twit = Tweet(
              user_id = self.bot['user_id'],
              bot_id = self.bot['id'],
              target = screen_name,
              text = full_text,
              translated = translated,
              entities = full_tweet._json,
              tweeted = 0,
              metrics = filtered_tweets[full_tweet.id_str]['metrics'],
            )
            db.session.add(twit)
            db.session.commit()
        
        print('[filtered Tweetes][Full]', filtered_tweets)
      # mark the target as analyzed.
      print(f"[Target]{target_info.data.username} Finished")
    except Exception as e:
      print('[Error] Timeline', screen_name, str(e))


  def satisfy_metrics(self, metrics):
    # if len(metrics.keys()) > 0:
    #   return False;
    if self.bot['type'] == 'ONE_TIME' and 'retweet' in self.bot['metrics'] and int(self.bot['metrics']['retweet']) > metrics['tweet']['retweets']:
      return False
    if 'follower' in self.bot['metrics'] and int(self.bot['metrics']['follower']) > metrics['followers']:
      return False
    if 'friend' in self.bot['metrics'] and int(self.bot['metrics']['friend']) > metrics['friends']: ## following
      return False
    if 'tweets' in self.bot['metrics'] and int(self.bot['metrics']['tweets']) > metrics['statuses']:
      return False
    if self.bot['type'] == 'ONE_TIME' and 'likes' in self.bot['metrics'] and int(self.bot['metrics']['likes']) > metrics['tweet']['favorite']:
      return False
    if 'lists' in self.bot['metrics'] and int(self.bot['metrics']['lists']) > metrics['listed']:
      return False
    return True

  def matches_keywords(self, text):
    for keyword in self.bot['exclusion_keywords']:
      if keyword in text:
        return False;
    
    for keyword in self.bot['inclusion_keywords']:
      if keyword in text:
        return True
    return True


  def parse_full_text(self, status):
    full_text = status.full_text
    entities = status.entities
    for url in entities['urls']:
      full_text = full_text.replace(url['url'], url['display_url'])
    return full_text

  def parse_full_text_v2(self, full_text, entities):
    for url in entities['urls']:
      full_text = full_text.replace(url['url'], url['display_url'])
    return full_text
  
  def postprocess_new_tweet(self, tweet, screen_name, metrics):
    ## reference for full text
    ## - https://docs.tweepy.org/en/latest/extended_tweets.html#handling-retweets
    ## - https://github.com/tweepy/tweepy/issues/974
    # full_text = self.parse_full_text_v2(tweet['full_text'], tweet['entities'])
    print('[Tweet]', tweet['retweeted_status'], tweet)
    full_text = self.parse_full_text_v2(tweet['full_text'] if tweet['retweet_count'] == 0 else tweet['retweeted_status']['full_text'], tweet['entities'])
    matches_keyword = self.matches_keywords(full_text)
    
    # check if text matches keywords(inclusion & exclusion)
    if not matches_keyword:
      print('[Metric] satisfied [Keywords] not satisfied.')
      return "Keyword match failed!"

    translated = translate(src_text=full_text)

    notification = {
      "user_name": screen_name,
      "bot": self.name,
      "tweet": tweet,
      # "tweet": tweet.text,
      "full": full_text,
      "translated": translated,
      "entities": tweet['entities'],
      # "extended_entities": tweet.extended_entities if 'extended_entities' in tweet else {},
      "retweeted": tweet['retweeted'],
      # "quote_count": tweet.quote_count,
      # "reply_count": tweet.reply_count,
      "retweet_count": tweet['retweet_count'],
      "favorite_count": tweet['favorite_count'],
    }
    io_notify_user(user_id=self.bot['user_id'], event=socket_event.NEW_TWEET_FOUND, args=notification)

    twit = Tweet(
      user_id = self.bot['user_id'],
      bot_id = self.bot['id'],
      target = screen_name,
      text = full_text,
      translated = translated,
      entities = tweet,
      tweeted = 0,
      metrics = metrics,
    )
    db.session.add(twit)
    db.session.commit()

  def format_time_v2(self, str_dt):
    dt_arr = str_dt.split(' ')
    return f"{dt_arr[0].strip()}T{dt_arr[1].strip()}:00Z"


  # def set_interval(self, func, sec):
  #   def func_wrapper():
  #     if not self.stopped:
  #       self.set_interval(self, func, sec)
  #       func()
  #   t = threading.Timer(self._interval, func_wrapper)
  #   t.start()
  #   return t

  # def processor(self):
  #   def func_wrapper():
  #     self.processor(self)

  #   if not self.stopped:
  #     threading.Timer(self._interval, self.processor).start()
  #     self._iterN += 1
  #     print('[Processing...] ' + str(self._iterN))
  #   else:
  #     pass


def run_bot(bot):
  str_bot_id = str(bot.id)
  if str_bot_id in botThreads and botThreads[str_bot_id].stopped:
    botThreads[str_bot_id].start()

  botThread = BotThread(bot)
  botThread.start()
  botThreads[str(bot.id)] = botThread
  return botThread


@app.route('/tasks/<id>/stop', methods=['GET', 'POST'])
def stop_bot_execution(id):
  try:
    if str(id) not in botThreads:
      raise Exception('Not found the bot running!')
    botThreads[str(id)].stop()
    # del botThreads[str(id)]

    bot = Bot.query.filter_by(id=id).first()
    if bot:
      bot.status = 'IDLE'
      bot.updated_at = datetime.utcnow()
      db.session.commit()
    return jsonify({
      "status": True,
      "message": "Bot has been stopped!",
    })
  except Exception as e:
    return jsonify({
      "status": False,
      "message": str(e)
    })


@app.route('/tasks/<id>/start', methods=['GET', 'POST'])
def start_bot_execution(id):
  bot = Bot.query.filter_by(id=id).first()
  if bot.status == 'RUNNING':
    return jsonify({
      "status": True,
      "message": "Bot already running!",
    })
  if not bot:
    return jsonify({
      "status": False,
      "message": "Not found the bot!",
    })

  botThread = BotThread(bot)
  botThread.start()
  botThreads[str(id)] = botThread
  bot.status = 'RUNNING'
  bot.updated_at = datetime.utcnow()
  db.session.commit()
  
  # botThread.start()
  return jsonify({
    "status": True,
    "message": "Success. Bot started.",
  })


@app.route('/tasks', methods=['POST'])
def add_new_bot():
  payload = request.get_json()
  bot_id = str(payload['id'])
  bot = BotDemo(name=payload['name'], interval=payload['interval'])
  botThread = BotThread(bot=bot)
  botThreads[bot_id] = botThread
  botThreads[bot_id].start()

  print('[PayLoad]', payload)
  return jsonify({
    "status": True,
    "message": "success",
  })

@app.route('/translate', methods=['POST'])
def test_translate():
  payload = request.get_json()
  txt = translate(src_text = payload['text'], target_lang = payload['lang'])
  return jsonify({ "text": txt })

