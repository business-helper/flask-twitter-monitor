from flask import jsonify, request
import threading
from marketingBot import app

botThreads = {}

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
  def __init__(self, bot, **args):
    threading.Thread.__init__(self)
    self.name = bot.name
    self._interval = bot.interval
    self.event = threading.Event()
    self.stopped = True
    

  def start(self):
    self.stopped = False
    self.execute_loop()

  def stop(self):
    self.stopped = True
    pass

  def execute_loop(self):
    def func_wrapper():
      self.execute_loop()
      self.processor()
    t = threading.Timer(self._interval, func_wrapper)
    t.start()

  def processor(self):
    self._iterN += 1
    print(f"[Processing] {self.name} {str(self._iterN)}")

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

bot1 = BotDemo(name='Bot I', interval=5)
botThread = BotThread(bot=bot1)
# botThread.start()
botThreads["1"] = botThread

@app.route('/tasks/<id>/stop', methods=['GET', 'POST'])
def stop_bot_execution(id):
  # global botThread
  botThread.stop()
  return jsonify({
    "status": True,
    "message": "success. bot stopped.",
  })

@app.route('/tasks/<id>/start', methods=['GET', 'POST'])
def start_bot_execution(id):
  # global botThread
  botThread.start()
  return jsonify({
    "status": True,
    "message": "success. bot started.",
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



