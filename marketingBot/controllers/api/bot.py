from flask import request, current_app, jsonify
from datetime import datetime

# from marketingBot.models import db
from marketingBot.models.Bot import db, Bot
from marketingBot.models.AppKey import AppKey
from marketingBot.controllers.api import api
from marketingBot.helpers.common import stringify
from marketingBot.helpers.wrapper import session_required

@api.route('/ping-bot', methods=['GET'])
def api_ping_bot():
  bot = Bot.query.filter_by(id=1).first()
  return jsonify({
    "status": True,
    "message": "pong",
    "data": bot.to_dict(),
  })

@api.route('/bots', methods=['GET'])
@session_required
def load_bots(self):
  skip = request.args.get('start')
  limit = request.args.get('length')
  # sortCol = request.args.get('order[0][column]')
  # sortDir = request.args.get('order[0][dir]')
  user_id = self.id
  # keyword = request.args.get('search[value]')

  bots = Bot.query.filter_by(user_id=user_id).limit(limit).offset(skip)
  app_keys = AppKey.query.filter_by(user_id=user_id).all()
  dict_keys = {}
  print('[App Keys]', app_keys)
  for app_key in app_keys:
    dict_keys[str(app_key.id)] = app_key.to_dict()
  print('[Keys]', dict_keys)
  data = []
  for idx, bot in enumerate(bots):
    bot = bot.format()
    bot_keys = []
    for key in bot.api_keys:
      key = str(key)
      if key in dict_keys:
        bot_keys.append(dict_keys[key])

    data.append([idx + 1, bot.name, bot.targets, bot_keys, bot.inclusion_keywords, bot.exclusion_keywords, bot.status, bot.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': 10,
    'iTotalDisplayRecords':10,
  })

@api.route('/bots', methods=['POST'])
@session_required
def create_bot(self):
  payload = dict(request.get_json())
  
  bot = Bot(
    user_id = self.id,
    name = payload['name'],
    api_keys = stringify(payload['api_keys']) if payload['api_keys'] else '[]',
    targets = stringify(payload['targets']) if payload['targets'] else '[]',
    inclusion_keywords = stringify(payload['inclusion_keywords']) if payload['inclusion_keywords'] else '[]',
    exclusion_keywords = stringify(payload['exclusion_keywords']) if payload['exclusion_keywords'] else '[]',
    status= payload['status'] if 'status' in payload else 'IDLE',
  )
  db.session.add(bot)
  db.session.commit()
  print('[Bot]', bot.to_dict(), bot.id)
  return jsonify({
    "status": True,
    "message": "A bot has been added!",
    "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
  })

@api.route('/bots/<id>', methods=['PUT'])
@session_required
def update_bot_by_id(self, id):
  payload = dict(request.get_json())
  bot = Bot.query.filter_by(id=id).first()
  bot.name = payload['name']
  bot.targets = stringify(payload['targets']) if 'targets' in payload else '[]'
  bot.api_keys = stringify(payload['api_keys']) if 'api_keys' in payload else '[]'
  bot.inclusion_keys = stringify(payload['inclusion_keys']) if 'inclusion_keys' in payload else '[]'
  bot.exclusion_keys = stringify(payload['exclusion_keys']) if 'exclusion_keys' in payload else '[]'


  db.session.commit()

  return jsonify({
    "status": True,
    "message": "A bot has been added!",
    "data": Bot.query.filter_by(id=bot.id).first().format().to_dict(),
  })

@api.route('/bots/<id>', methods=['GET'])
@session_required
def get_bot_by_id(self, id):
  bot = Bot.query.filter_by(id=id).first()
  if not bot:
    return jsonify({
      "status": False,
      "message": "Bot does not exist!",
    })
  return jsonify({
    "status": True,
    "message": "success",
    "data": bot.format().to_dict(),
  })



