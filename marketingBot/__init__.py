# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask('marketingBot')
toolbar = DebugToolbarExtension(app)
app.config.from_object('marketingBot.config.app.DBConfig')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/twitter_bot'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
#     os.getenv('DB_USER', 'flask'),
#     os.getenv('DB_PASSWORD', ''),
#     os.getenv('DB_HOST', 'mysql'),
#     os.getenv('DB_NAME', 'flask')
# )

from marketingBot.models import db
db.init_app(app)

# app.config['SECRET_KEY'] = 'random'
app.debug = True



from marketingBot.controllers import *
