# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask('marketingBot')
toolbar = DebugToolbarExtension(app)
app.config.from_object('marketingBot.config.app.DBConfig')

from marketingBot.models import db
db.init_app(app)

# app.config['SECRET_KEY'] = 'random'
app.debug = False

from marketingBot.controllers import *
