from datetime import datetime
from flask import jsonify, request
from sqlalchemy.sql import text
import threading
import tweepy
import threading
from pytwitter import Api
# from uwsgidecorators import *

from marketingBot import db, app
from marketingBot.config.constants import socket_event
from marketingBot.controllers.socket import io_notify_user
from marketingBot.models.Bot import Bot
from marketingBot.models.AppKey import AppKey
from marketingBot.models.Notification import Notification
from marketingBot.models.Tweet import Tweet
from marketingBot.helpers.common import translate, translate_google

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

class TweetAction():
  def __init__(self, instance, bot_object = {}, ranks = []):
    self.api = instance
    self.bot = bot_object
    ranks.sort(reverse = True)
    self.ranks = ranks

  def getRank(self, rank_index):
    try:
      index = self.ranks.index(rank_index)
      return index + 1
    except Exception as e:
      print(f"[TweetAction][GetRank] Error: {str(e)}")
      return len(self.ranks) + 2

  def generateDefaultText(self, tweet_obj):
    try:
      default_text = self.bot['default_text']
      # link = f"https://twitter.com/{tweet_obj['entities']['user']['screen_name']}/status/{tweet_obj['entities']['id_str']}"
      account = f"@{tweet_obj['entities']['user']['screen_name']}"

      updated_text = default_text.replace('$account$', account).replace('$link$', '')
      if len(list(self.bot['rank_factors'].keys())) > 0:
        rank = self.getRank(tweet_obj['rank_index'])
        updated_text = updated_text.replace('$rank$', str(rank))
      else:
        updated_text = updated_text.replace('$rank$', '')
      print(f"[Generate Default Text] from '{default_text}' to '{updated_text}']")
      return updated_text
    except Exception as e:
      print(f"[Generate Default Text][Error] {str(e)}", e)
      return '';

  def getAttachment(self, tweet_obj, initial = []):
    link = f"https://twitter.com/{tweet_obj['entities']['user']['screen_name']}/status/{tweet_obj['entities']['id_str']}"
    if '$link$' in self.bot['default_text'] and link not in initial:
      initial.append(link)
    return initial[0] if len(initial) >= 0 else None

  def makeAction(self, id, action):
    if action == 'tweet':
      return self.tweet(id)
    elif action == 'retweet':
      return self.retweet(id)
    elif action == 'comment':
      return self.comment(id)
    elif action == 'quote':
      return self.quote(id)
    else:
      return False

  def tweet(self, id, media = []):
    tweet = Tweet.query.filter_by(id = id).first()
    try:
      if not tweet:
        raise Exception(f"Not found the tweet with id {id}")

      default_text = self.generateDefaultText(tweet.to_dict())
      print(f"[Default Text][Final] {default_text}")
      attachment = self.getAttachment(tweet.to_dict(), initial = [])

      self.api.update_status(f"{default_text} {tweet.translated}", media_ids = media, attachment_url = attachment)

      tweet.updated_at = datetime.utcnow()
      tweet.tweeted = 2
      db.session.commit()
      return True
    except Exception as e:
      print(f"[TweetAction][Tweet] error: ", str(e), e)
      db.session.commit()
      return False

  def retweet(self, id):
    tweet = Tweet.query.filter_by(id = id).first()
    try:
      if not tweet:
        raise Exception(f"Not found the tweet with id {id}")
      self.api.retweet(tweet.entities['id_str'])

      tweet.updated_at = datetime.utcnow()
      tweet.tweeted = 1
      db.session.commit()
      return True
    except Exception as e:
      print(f"[TweetAction][Retweet] error: ", str(e))
      db.session.commit()
      return False

  def comment(self, id, comment = False, media = []):
    tweet = Tweet.query.filter_by(id = id).first()
    try:
      if not tweet:
        raise Exception(f"Not found the tweet with id {id}")

      default_text = self.generateDefaultText(tweet.to_dict())
      attachment = self.getAttachment(tweet.to_dict(), initial = [])
      comment = tweet.translated if not comment else comment
      self.api.update_status(
        f"@{tweet.entities['user']['screen_name']} {default_text} {comment}",
        media_ids = media,
        in_reply_to_status_id = tweet.entities['id_str'],
        attachment_url = attachment,
      )
      tweet.updated_at = datetime.utcnow()
      tweet.tweeted = 3
      db.session.commit()
      return True
    except Exception as e:
      print(f"[TweetAction][Comment] error: {str(e)}")
      db.session.commit()
      return False

  def quote(self, id, comment = False, media = []):
    tweet = Tweet.query.filter_by(id = id).first()
    try:
      if not tweet:
        raise Exception(f"Not found the tweet with id {id}")
      default_text = self.generateDefaultText(tweet.to_dict())
      target_tweet_url = f"https://twitter.com/{tweet.entities['user']['screen_name']}/status/{tweet.entities['id_str']}"
      attachment = self.getAttachment(tweet.to_dict(), initial = [target_tweet_url])
      print(f"[Attachment]", attachment)
      comment = comment if comment else tweet.translated
      self.api.update_status(
        f"{default_text} {comment} {target_tweet_url}",
        media_ids = media,
        attachment_url = attachment,
      )
      tweet.updated_at = datetime.utcnow()
      tweet.tweeted = 4
      db.session.commit()
      return True
    except Exception as e:
      print(f"[TweetAction][Quote]{id} error: {str(e)}", e)
      db.session.commit()
      return False



class BotThread(threading.Thread):
  thread = None
  stopped = True
  _iterN = 0

  name = ''
  identifier = 0
  _interval = 5
  bot = None
  apis = []
  apis_v2 = []
  targets = {}
  last_tweet_ids = {}
  one_time_batch = 10
  from_schedule = False

  def __init__(self, bot, from_schedule = False, identifier = 0, **args):
    threading.Thread.__init__(self)
    self.name = bot['name']
    self.identifier = identifier
    self._interval = bot['period']
    self.bot = bot
    # self.event = threading.Event()
    self.stopped = True
    self.from_schedule = from_schedule
    for screen_name in self.bot['targets']:
      self.last_tweet_ids[screen_name.strip()] = {
        "now": None,
        "prev": None,
      }
    # self.apis = self.apis_v2 = self.targets = self.last_tweet_ids = []

  # @basic
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

  # @basic
  def create_apis(self):
    print('[API Keys]', self.bot['api_keys'], type(self.bot['api_keys']))
    if len(self.bot['api_keys']) > 0:
      for api_key_id in self.bot['api_keys']:
        api_key = AppKey.query.filter_by(id=api_key_id).first()

        api_instance = self.create_tweepy_instance(api_key.consumer_key, api_key.consumer_secret, api_key.access_token, api_key.access_token_secret)
        if not api_instance:
          return print('[API Instance] Failed to create.', api_key_id)
        self.apis.append(api_instance)

  # @basic
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

  # @operator
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

  # @operator
  def stop(self):
    print(f"[Task] stopping '{self.name}'")
    self.stopped = True


  # @real-time
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

  # @real-time
  def execute_loop(self):
    def func_wrapper():
      if self.stopped:
        return False
      self.execute_loop()
      self.processor()
    t = threading.Timer(self._interval * len(self.apis), func_wrapper)
    t.start()

  # @real-time
  def processor(self):
    print(f"[Processing] {self.name} {str(self._iterN)}")
    self.monitor_accounts()

  # @real-time
  def monitor_accounts(self):
    print(f"[MonitorAccount]', Interval: {self._interval}s, APIs: {len(self.apis)}")

    for idx, api in enumerate(self.apis):
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

  # @real-time
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


  # @one-time
  def start_one_time_batch(self):
    try:
      if len(self.apis_v2) > 0:
        api_inst = self.apis_v2[0]
        for screen_name in self.bot['targets']:
          if self.stopped:
            break
          self.analyze_target(screen_name = screen_name, api_inst = api_inst)
      else:
        print(f"[Bot][{self.bot['name']}]No available API v2 instances")

      # cutout by the limitation
      final_ids = self.process_cutout()
      self.do_translation(final_ids)
      self.process_automation(final_ids)
      # after the bot is finished or stopped by error.
      bot = Bot.query.filter_by(id = self.bot['id']).first()
      if bot:
        bot.status = 'IDLE'
        bot.updated_at = datetime.utcnow()
        db.session.commit()
      print(f"[BotThread][One Time Bot][Finished] {bot.id}-{bot.name}")

      notification_msg = f"The bot [{bot.name}] finished!"
      notification = Notification(
        user_id = bot.user_id,
        text = notification_msg,
        bot_id = bot.id,
        payload = {
          "type": "BOT_FINISHED",
          "bot": bot.id,
        },
      )
      db.session.add(notification)
      db.session.commit()

      io_notify_user(
        user_id = bot.user_id,
        event = socket_event.BOT_FINISHED,
        args = { "message": notification_msg },
      )
      db.session.remove()
    except Exception as e:
      print(f"[One Time Bot Error]  {str(e)}")
      db.session.remove()
      pass

  # @one-time
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

    now = datetime.now() #pytz.timezone('Asia/Tokyo')
    start_time0 = now
    if self.from_schedule and self.bot['schedule_time']:
      start_time0 = datetime.fromisoformat(self.bot['schedule_time'])
      # start_time0.astimezone(pytz.timezone('Asia/Tokyo'))
    delta = now - start_time0
    start_time = self.format_time_v2(self.bot['start_time'], delta)
    end_time = self.format_time_v2(self.bot['end_time'], delta)
    print('[Start & End Time]', start_time, end_time)
    # since_id = None #"1408485784840065028"
    try:
      while(True):
        if self.stopped:
          return False
        # if start time is later than end time, then break;
        if start_time > end_time:
          break;
        
        timelines = False
        try:
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
        except Exception as e:
          print('[Timelines][Error]', str(e))
          break

        print('[timelines]', len(timelines.data))
        # print('[End Time] Old: ', end_time)
        end_time = timelines.data[len(timelines.data) - 1].created_at
        # print('[End Time] New: ', end_time)

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

        # check if the bot has stopped.
        if self.stopped:
          return False

        full_tweets = api_v1.statuses_lookup(id_=filtered_tweet_ids, tweet_mode = 'extended')
        # print('[Full Tweets]', full_tweets)
        for full_tweet in full_tweets:
          if self.stopped:
            return False
          full_text = self.parse_full_text(full_tweet)
          # filtered_tweets[full_tweet.id_str]['full_text'] = full_text
          # filtered_tweets[full_tweet.id_str]['keyword_match'] = self.matches_keywords(full_text)
          # filtered_tweets[full_tweet.id_star] = {
          #   "full_text": full_text,
          #   "keyword_matched": self.matches_keywords(full_text),
          #   "entities": full_text._json,
          # }

          if self.matches_keywords(full_text):
            twit_dict = dict(
              user_id = self.bot['user_id'],
              bot_id = self.bot['id'],
              target = screen_name,
              text = full_text,
              translated = full_text,
              entities = full_tweet._json,
              tweeted = 0,
              metrics = filtered_tweets[full_tweet.id_str]['metrics'],
            )
            self.check_insert_tweet(twit_dict)
        
        # print('[filtered Tweetes][Full]', filtered_tweets)
      # mark the target as analyzed.
      print('[Finished]')
      print(f"[Target]{target_info.data.username} Finished")
    except Exception as e:
      # exc_type, exc_obj, exc_tb = sys.exc_info()
      # tb = traceback.extract_tb(exc_tb)[-1]
      # print(exc_type, tb[2], tb[1])
      print('[Error] Timeline: ', screen_name, str(e))
      self.stop_bot_by_error(e)
      # raise e


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
    
    if len(self.bot['inclusion_keywords']) == 0:
      return True
    for keyword in self.bot['inclusion_keywords']:
      if keyword in text:
        return True
    return False

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

    lang = self.bot['target_langs'][screen_name] if screen_name in self.bot['target_langs'] and self.bot['target_langs'][screen_name] != 'NONE' else 'JA'
    translated = translate(src_text=full_text, target_lang = lang) if self.bot['enable_translation'] and lang != 'NONE' else full_text

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

    # twit = Tweet(
    twit_dict = dict(
      user_id = self.bot['user_id'],
      bot_id = self.bot['id'],
      target = screen_name,
      text = full_text,
      translated = translated,
      entities = tweet,
      tweeted = 0,
      metrics = metrics,
    )
    self.check_insert_tweet(twit_dict)
    # db.session.add(twit)
    # db.session.commit()

  def format_time_v2(self, str_dt, delta):
    # print('[Format Time][Delta]', delta)
    # ref: https://medium.com/easyread/understanding-about-rfc-3339-for-datetime-formatting-in-software-engineering-940aa5d5f68a
    dt_arr = str_dt.split(' ')
    # dt = datetime.fromisoformat('2010-11-06T00:00:00+09:00')
    # dt.isoformat
    # return f"{dt_arr[0].strip()}T{dt_arr[1].strip()}:00Z"
    dt = datetime.fromisoformat(f"{dt_arr[0].strip()}T{dt_arr[1].strip()}:00+09:00") + delta
    return f"{dt.year}-{str(dt.month).zfill(2)}-{str(dt.day).zfill(2)}T{str(dt.hour).zfill(2)}:{str(dt.minute).zfill(2)}:{str(dt.second).zfill(2)}+09:00"

  def check_insert_tweet(self, twit_dict):
    # db.session.query(Tweet).filter(Tweet.entities['id_str'] == id).first()
    tweet = db.session.query(Tweet).filter(
      Tweet.entities['id_str'] == twit_dict['entities']['id_str'],
      Tweet.user_id == twit_dict['user_id'],
      Tweet.bot_id == twit_dict['bot_id'],
      Tweet.session == self.identifier,
    ).first()

    # calculate rank index
    twit_dict['rank_index'] = self.calculate_rank_index(twit_dict)

    if not tweet:
      twit = Tweet(**twit_dict, session = self.identifier)
      db.session.add(twit)
      db.session.commit()
      print('[Check & Insert Tweet][Inserted]')
    else:
      tweet.session = self.identifier
      tweet.metrics = twit_dict['metrics']
      tweet.entities = twit_dict['entities']
      tweet.rank_index = twit_dict['rank_index']
      tweet.updated_at = datetime.utcnow()
      db.session.commit()
      print('[Check & Insert Tweet][Updated]')

  def calculate_rank_index(self, twit_dict):
    rank_factors = self.bot['rank_factors']
    metrics = twit_dict['metrics']

    followers = metrics['followers'] if 'followers' in metrics else 0
    likes = metrics['tweet']['favorite'] if 'favorite' in metrics['tweet'] else 0
    comments = metrics['tweet']['quotes'] if 'quotes' in metrics['tweet'] else 0
    retweets = metrics['tweet']['retweets'] if 'retweets' in metrics['tweet'] else 0
    numerator_val = {
      "retweets": retweets,
      "likes": likes,
      "comments": comments,
    }

    denominator_val = {
      "followers": followers,
    }

    numerator = 0
    for key in numerator_val.keys():
      if rank_factors[key]:
        numerator += numerator_val[key]
    denominator = denominator_val['followers'] if rank_factors['followers'] else 1

    if denominator == 0:
      return 0
    return numerator / denominator

  def process_cutout(self):
    print('[Bot][Cutout] Starting...')
    if self.bot['enable_cutout'] and self.bot['cutout'] > 0:
      order_by = text(f"rank_index desc")
      condition = {
        "user_id": self.bot['user_id'],
        "bot_id": self.bot['id'],
        "session": self.identifier,
      }
      total = db.session.query(Tweet).filter_by(**condition).count()
      print(f"[Bot][Cutout] collected {total} tweets")
      tweets = db.session.query(Tweet).filter_by(**condition).order_by(order_by).limit(self.bot['cutout']).offset(0)
      final_ids = list(map(lambda tweet: tweet.id, tweets))
      print('[Bot][Cutout] Will leave', final_ids)
      db.session.commit()

      if total > len(final_ids):
        tweets_to_delete = db.session.query(Tweet).filter(Tweet.id.notin_(final_ids)).filter(Tweet.bot_id == self.bot['id']).filter(Tweet.session == self.identifier)
        # tweets_to_delete.delete(synchronize_session=False)
        for tweet in tweets_to_delete:
          db.session.delete(tweet)
        db.session.commit()
        db.session.remove()
      print('[Bot][Cutout] Finished')
      return final_ids
    return False

  def do_translation(self, final_ids = False):
    # get all tweets(after cutout)
    tweets = Tweet.query.filter_by(bot_id = self.bot['id'], session = self.identifier).all()
    tweet_ids = list(map(lambda tweet: tweet.id, tweets)) if final_ids == False else final_ids
    print(f"[Translation] Will translate {len(tweet_ids)} tweets", tweet_ids)
    for tweet_id in tweet_ids:
      tweet = Tweet.query.filter_by(id = tweet_id).first()
      lang = self.bot['target_langs'][tweet.target] if tweet.target in self.bot['target_langs'] else 'JA'
      translation_method = translate if self.bot['translator'] == 'DEEPL' else translate_google
      tweet.translated = translation_method(src_text = tweet.text, target_lang = lang) if self.bot['enable_translation'] and lang != 'NONE' else tweet.text    
      tweet.updated_at = datetime.utcnow()
      db.session.commit()
    return tweet_ids

  def process_automation(self, final_ids = False):
    print(f"[Automation]")
    allowed_actions = ['tweet', 'retweet', 'comment', 'quote']

    # automation must be applied for one-time bot enabled automation.
    if self.bot['type'] == 'REAL_TIME' or not self.bot['enable_automation']:
      return False
    
    # automation action should be valid, must be in allowed actions.
    if self.bot['auto_action'] not in allowed_actions:
      return False

    # get all tweets(after cutout)
    tweets = Tweet.query.filter_by(bot_id = self.bot['id'], session = self.identifier).all()
    tweet_ids = list(map(lambda tweet: tweet.id, tweets)) if final_ids == False else final_ids
    # get rank indices
    rank_indices = []
    for twit in tweets:
      if twit.id in tweet_ids:
        rank_indices.append(str(twit.rank_index))

    db.session.commit()
    print(f"[Bot][{self.bot['name']}]", len(tweets), tweet_ids, rank_indices)
    tweetAction = TweetAction(instance = self.apis[0], bot_object = self.bot, ranks = rank_indices)
    for tweet_id in tweet_ids:
      tweetAction.makeAction(id = tweet_id, action = self.bot['auto_action'])

  def stop_bot_by_error(self, e):
    self.stopped = True
    bot = Bot.query.filter_by(id = self.bot['id']).first()
    bot.status = 'IDLE'
    bot.updated_at = datetime.utcnow()
    db.session.commit()

    
    notification_msg = f"The bot [{bot.name}] has stopped with Error '{str(e)}'!"
    notification = Notification(
      user_id = self.bot['user_id'],
      text = notification_msg,
      bot_id = self.bot['id'],
      payload = {
        "type": "RUNTIME_ERROR",
        "bot": self.bot['id'],
      },
    )
    db.session.add(notification)
    db.session.commit()

    # emit socket event
    io_notify_user(
      user_id = self.bot['user_id'],
      event = socket_event.BOT_STOPPED,
      args = { "message": notification_msg },
    )



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
  if not bot:
    return jsonify({
      "status": False,
      "message": "Not found the bot!",
    })
  if bot.status == 'RUNNING':
    return jsonify({
      "status": True,
      "message": "Bot already running!",
    })

  run_bot_as_thread(id = id, from_schedule = False)
  
  # botThread.start()
  return jsonify({
    "status": True,
    "message": "Success. Bot started.",
  })


@app.route('/translate', methods=['POST'])
def test_translate():
  payload = request.get_json()
  txt = translate_google(src_text = payload['text'], target_lang = payload['lang'])
  return jsonify({ "text": txt })


def run_bot_as_thread(id, from_schedule = True):
  print(f"[Run Bot As Thread] {id} at {str(datetime.utcnow())}, [scheduled] {str(from_schedule)}")
  # to-do: analyze
  # if bot.status == 'RUNNING':
  #   print('[Run as Thread][Bot]', bot.to_dict())
  #   print(f"[Cron][BOt]{id} Stopped: already running")
  #   return True
  try:
    bot = Bot.query.filter_by(id=id).first()
    if not bot:
      print(f"[Cron][Bot]{id} Not Fouond...")
      raise Exception(f"[Cron][Bot]{id} Not Fouond...")
      # return False

    bot_user_id = bot.user_id
    # update db
    bot.status = 'RUNNING'
    bot.udpated_at = datetime.utcnow()
    db.session.commit()

    notification_msg = f"The bot [{bot.name}] has been triggered by schedule!" if from_schedule else f"You started the bot [{bot.name}]!"
    notification = Notification(
      user_id = bot.user_id,
      text = notification_msg,
      bot_id = id,
      payload = {
        "type": "SCHEDULE_RUN" if from_schedule else "BOT_RUN",
        "bot": bot.id,
      },
    )
    db.session.add(notification)
    db.session.commit()
    db.session.flush()
    identifier = notification.id
    print('[Notification ID]', identifier)
    
    def run_botThread(bot_id):
      print(f"[run_botThread] bot {bot_id}")

      bot = Bot.query.filter_by(id=bot_id).first()
      bot_obj = bot.to_dict()
      db.session.expire(bot)
      
      botThread = BotThread(bot= bot_obj, from_schedule = from_schedule, identifier = identifier)
      botThreads[str(bot_id)] = botThread
      botThread.start()
    threading.Thread(target = run_botThread, args=[id]).start()

    # emit socket event
    io_notify_user(
      user_id = bot_user_id,
      event = socket_event.BOT_SCHEDULE_START if from_schedule else socket_event.BOT_MANUAL_START,
      args = { "message": notification_msg },
    )

  except Exception as e:
    print(f"[Cron][Bot]{id} Stopped By Error", str(e))
    bot = Bot.query.filter_by(id=id).first()
    bot.status = 'IDLE'
    bot.updated_at = datetime.utcnow()
    # db.session.add(bot)
    db.session.commit()
    return False
