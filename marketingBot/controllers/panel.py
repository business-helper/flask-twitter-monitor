from flask import Flask, render_template, jsonify, redirect, url_for, escape, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask import flash

from marketingBot import app
from marketingBot.models.AppKey import db, AppKey
from marketingBot.models.Bot import Bot
from marketingBot.helpers.common import unset_login_session, validate_session, timestamp
from marketingBot.helpers.wrapper import session_required

@app.route('/ping')
def ping():
  print('[Ping] requested')
  return jsonify({ "status": True, "message": "Pong" })

@app.route('/dashboard', methods=['GET'])
@session_required
def dashboard(self):
  return render_template('panel/dashboard.html')

@app.route('/api-apps')
@session_required
def api_apps(self):
  return render_template('panel/api-apps.html')


@app.route('/load-api-apps')
@session_required
def load_api_apps(self):
  skip = request.args.get('start')
  limit = request.args.get('length')
  sortCol = request.args.get('order[0][column]')
  sortDir = request.args.get('order[0][dir]')
  user_id = self.id
  keyword = request.args.get('search[value]')

  apps = AppKey.query.filter_by(user_id=user_id).limit(limit).offset(skip)
  
  data = []
  for idx, app in enumerate(apps):
    data.append([idx + 1, app.name, f"{app.consumer_key}:{app.consumer_secret}:{app.access_token}:{app.access_token_secret}", app.valid, app.id])

  return jsonify({
    'data': data,
    'draw': request.args.get('draw'),
    'iTotalRecords': 10,
    'iTotalDisplayRecords':10,
  })


# Add a new API app.
@app.route('/api-app', methods=['POST'])
@session_required
def add_api_app(self):
  payload = request.get_json()
  print('[Payload]', payload)
  isExist = AppKey.query.filter_by(consumer_key=payload['consumer_key'], consumer_secret=payload['consumer_secret']).first()
  if (isExist):
    # flash('This API app already exists!')
    # return render_template('panel/api-apps.html')
    return jsonify({
      "status": False,
      "message": "This API app already exists!",
    })
  print('[Active]', payload['valid'])
  appKey = AppKey(
    user_id = self.id,
    consumer_key = payload['consumer_key'],
    consumer_secret = payload['consumer_secret'],
    access_token = payload['access_token'],
    access_token_secret = payload['access_token_secret'],
    name = payload['name'],
    valid = payload['valid'],
  )
  db.session.add(appKey)
  db.session.commit()
  # return render_template('panel/api-apps.html')
  return jsonify({
    "status": True,
    "message": "Data has been added!",
  })


@app.route('/bots', methods=['GET'])
@session_required
def bots_page(self):
  api_keys = AppKey.query.filter_by(user_id=self.id,valid=True).all()
  apps = []
  for api_key in api_keys:
    apps.append(api_key.to_dict())
  # for ap in apps:
  #   print('[Type]', type(ap))
  print('[Apps]', apps)
  data = {
    "time": timestamp(),
    "api_apps": apps,
    "names": ['A', 'B']
  }
  return render_template('panel/bots.html', data=data)