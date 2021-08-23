from flask import session, json, Response
import os
import requests
import time
import csv
from googletrans import Translator
from twitter_text import parse_tweet

from marketingBot import app
from marketingBot.config.constants import mPath
from marketingBot.models.User import User

google_translator = Translator()

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
  print('[Translation]', target_lang,data)
  if 'translations' in data:
    return data['translations'][0]['text']

  raise Exception(data['message'])

def translate_google(src_text, target_lang = 'JA'):
  try:
    if target_lang.upper() == 'ZH':
      target_lang = 'ZH-CN'
    res = google_translator.translate(src_text, dest = target_lang)
    return res.__dict__()['text']
  except Exception as e:
    print('')

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

def save_as_csv(headers, data_array = [], user_id = 0):
  file_name = f"Tweets-{user_id}-{int(time.time())}.csv"
  rel_path = os.path.join(mPath.CSV_PATH, file_name)
  dest_path = os.path.join(app.root_path, rel_path)

  # csv_writer = csv.writer(dest_path, 'wb')

  csv = f"No,{','.join(headers)}"
  for idx, data in enumerate(data_array):
    csv = f"{csv}\n{idx + 1}"
    for val in data:
      csv = f"{csv},{val}"
  # csv = '1,2,3\n4,5,6\n'

  with open(dest_path, 'w', encoding='UTF-8', newline='') as f:
    f.write(csv)
  return file_name

def download_csv(headers, data_array = [], file_name = 'Tweets.csv'):
  csv = f"No,{','.join(headers)}"
  for idx, data in enumerate(data_array):
    csv = f"{csv}\n{idx + 1}"
    for val in data:
      csv = f"{csv},{val}"
  # csv = '1,2,3\n4,5,6\n'
  return Response(
    csv,
    mimetype="text/csv",
    headers={
      "Content-disposition": f"attachment; filename={file_name}"
    }
  )

def tweet_substring(text, length, skip):
  pos = skip + 1
  while(parse_tweet(text[skip:pos]).weightedLength <= length and pos < len(text)):
    pos = pos + 1
  return {
    "pos": pos,
    "text": text[skip:pos],
  }

def split_tweet(text, default_text):
  MAX_LENGTH = 280
  tot_text = f"{default_text} {text}"
  tot_length = parse_tweet(tot_text).weightedLength

  if (tot_length) < MAX_LENGTH:
    return [
      f"{default_text} {text}"
    ]
  else:
    texts = []
    skip = 0
    length = MAX_LENGTH - len('i/n') - 20
    while True:
      result = tweet_substring(tot_text, length, skip)
      texts.append(result['text'])
      skip = result['pos']
      if skip >= len(tot_text):
        break
    
    for i, text in enumerate(texts):
      texts[i] = f"{str(i + 1)}/{str(len(texts))} {texts[i]}"
    return texts
