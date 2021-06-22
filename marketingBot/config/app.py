import os
from dotenv import load_dotenv
load_dotenv()

class DBConfig(object):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER'),
    os.getenv('DB_PASSWORD'),
    os.getenv('DB_HOST'),
    os.getenv('DB_NAME')
  )
  SECRET_KEY = 'marketing_bot_!@#'
  SQLALCHEMY_TRACK_MODIFICATIONS = False