from flask import Flask, session, render_template, redirect, url_for, escape, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask import flash

from marketingBot import app
from marketingBot.models.User import db, User
from marketingBot.helpers.common import unset_login_session, validate_session
from marketingBot.helpers.wrapper import session_required



@app.route('/dashboard', methods=['GET'])
@session_required
def dashboard(self):

  return render_template('panel/dashboard.html')
