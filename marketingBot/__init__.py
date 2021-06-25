# -*- coding: utf-8 -*-
__version__ = '0.1'
import os
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask('marketingBot')
toolbar = DebugToolbarExtension(app)
app.config.from_object('marketingBot.config.app.DBConfig')

from marketingBot.models import db
db.init_app(app)

# organizing routes
from marketingBot.controllers.api import api
app.register_blueprint(api, url_prefix='/api')


# app.config['SECRET_KEY'] = 'random'
app.debug = os.getenv('DEBUG')

from marketingBot.controllers import *
