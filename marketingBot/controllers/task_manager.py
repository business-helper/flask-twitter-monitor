from datetime import datetime
from flask import jsonify, request
import threading
import tweepy

from marketingBot import app
from marketingBot.models.Bot import db, Bot
from marketingBot.models.AppKey import AppKey

botThreads = {}

def initialize_bots():
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
  name = ''
  thread = None
  _interval = 5
  stopped = True
  _iterN = 0
  apis = []
  targets = []
  def __init__(self, bot, **args):
    threading.Thread.__init__(self)
    self.name = bot.name
    self._interval = bot.period
    self.bot = bot.to_dict()
    # self.event = threading.Event()
    self.stopped = True
    self.apis = []
    
  def start(self):
    print(f"[Task] starting '{self.name}'")
    self.stopped = False
    self.create_apis()
    self.validate_targets()
    self.execute_loop()

  def stop(self):
    print(f"[Task] stopping '{self.name}'")
    self.stopped = True


  def create_apis(self):
    print('[API Keys]', self.bot['api_keys'], type(self.bot['api_keys']))
    if len(self.bot['api_keys']) > 0:
      for api_key_id in self.bot['api_keys']:
        api_key = AppKey.query.filter_by(id=api_key_id).first()

        api_instance = self.create_tweepy_instance(api_key.consumer_key, api_key.consumer_secret, api_key.access_token, api_key.access_token_secret)
        if not api_instance:
          return print('[API Instance] Failed to create.', api_key_id)
        self.apis.append(api_instance)
    
  def validate_targets(self):
    if len(self.apis) == 0:
      return []
    for user_id in self.bot['targets']:
      try:
        user = self.apis[0].get_user(user_id)
        self.targets.append(user.id)
      except Exception as e:
        pass
    print('[Targets]', type(self.bot['targets']), self.bot['targets'], self.targets)
      

  def execute_loop(self):
    def func_wrapper():
      if self.stopped:
        return False
      self.execute_loop()
      self.processor()
    t = threading.Timer(self._interval, func_wrapper)
    t.start()

  def processor(self):
    self._iterN += 1
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
    for api in self.apis:
      if len(self.bot['targets']) > 0:
        try:
          users = api.lookup_users(self.targets)
          # print('[LookUp] Statuses ', users[0].status)
          print(f"[MonitorResult] {len(users)} targets, IDs: {list(map(lambda user:user.status.id, users))}")
        except Exception as e:
          print('[LookUp] Error ', str(e))
          return False

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



