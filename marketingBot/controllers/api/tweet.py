from flask import request, current_app, jsonify
from datetime import datetime

# from marketingBot.models import db
from marketingBot.models.Bot import db, Bot
from marketingBot.models.Tweet import Tweet
from marketingBot.controllers.api import api
from marketingBot.controllers.task_manager import start_bot_execution, stop_bot_execution
from marketingBot.helpers.common import stringify, splitString2Array, json_parse
from marketingBot.helpers.wrapper import session_required

def add_tweet(data):
  tweet = Tweet(
    user_id = data['user_id'],
    bot_id = data['bot_id'],
    target = data['target'],
    text = data['text'],
    entities = data['entities'],
  )

