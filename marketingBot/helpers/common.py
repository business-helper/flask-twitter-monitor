from flask import session, json
import os
import requests
import time

from marketingBot.models.User import User

deepl_endpoint = {
  "free": 'https://api-free.deepl.com/v2',
  "pro": 'https://api-free.deepl.com/v2',
}
deepl_key = os.getenv('DEEPL_KEY')
deepl_free = os.getenv('DEEPL_FREE')

translation_endpoint = deepl_endpoint['free'] if deepl_free else deepl_endpoint['pro']

def set_login_session(user):
  if not user:
    raise Exception('Invalid User!')
  session['login'] = True
  session['user_id'] = user.id
  session['user_email'] = user.email

def unset_login_session():
  session['login'] = None
  session['user_id'] = None
  session['user_email'] = None

def validate_session():
  if ('login' not in session) or not session['login']:
    unset_login_session()
    return False
  elif 'user_email' in session:
    user = User.query.filter_by(email=session['user_email']).first()
    if user:
      return user
    else:
      return False
  else:
    return False

def timestamp():
  return int(time.time() * 1000)

def stringify(data):
  return json.dumps(data, separators=(',', ':'))

def json_parse(str):
  return json.loads(str)

def translate(src_text, target_lang = 'JA'):
  url = f"{translation_endpoint}/translate"
  params = {
    "auth_key": deepl_key,
    "text": src_text,
    "target_lang": target_lang,
  }
  res = requests.get(url = url, params = params)
  data = res.json()
  return data['translations'][0]['text']

def splitString2Array(str):
  try:
    if not str:
      return []

    strings = []
    # split by line
    lines = str.splitlines()
    for line in lines:
      words = line.split(',')
      for word in words:
        word = word.strip()
        if not word:
          pass
        strings.append(word)
    return strings
  except Exception as e:
    return []

