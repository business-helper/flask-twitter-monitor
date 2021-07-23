from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marketingBot import app
db = SQLAlchemy(app)

from marketingBot.helpers.common import json_parse

class Bot(db.Model):
  __tablename__ = 'bots'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(50), nullable=False)
  type = db.Column(db.String(10), nullable=False)
  api_keys = db.Column(db.JSON)
  targets = db.Column(db.JSON)
  inclusion_keywords = db.Column(db.JSON)
  exclusion_keywords = db.Column(db.JSON)
  period = db.Column(db.Numeric(5, 1))
  start_time = db.Column(db.String(30), nullable=True)
  end_time = db.Column(db.String(30), nullable=True)
  schedule_interval = db.Column(db.Integer, default=0)
  schedule_time = db.Column(db.String(30), nullable=False)
  enable_translation = db.Column(db.Boolean, default=True)
  target_langs = db.Column(db.JSON)
  metrics = db.Column(db.JSON)
  rank_factors = db.Column(db.JSON)
  enable_cutout = db.Column(db.Boolean, default = False)
  cutout = db.Column(db.Integer, default = 0)
  last_tweets = db.Column(db.JSON)
  status = db.Column(db.String(20), default='IDLE')
  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, name, type, api_keys, targets, inclusion_keywords, exclusion_keywords, 
    period, status, start_time, end_time,
    metrics = {}, schedule_interval = 0, schedule_time = 0, last_tweets = [], rank_factors = {},
    enable_translation = True, target_langs = {}, enable_cutout = False, cutout = 0,
    **args):

    self.user_id = user_id
    self.name = name
    self.type = type
    self.api_keys = api_keys
    self.targets = targets
    self.inclusion_keywords = inclusion_keywords
    self.exclusion_keywords = exclusion_keywords
    self.period = period
    self.start_time = start_time
    self.end_time = end_time
    self.schedule_interval = schedule_interval
    self.schedule_time = schedule_time
    self.metrics = metrics
    self.rank_factors = rank_factors
    self.status = status
    self.last_tweets = last_tweets
    self.enable_translation = enable_translation
    self.target_langs = target_langs
    self.enable_cutout = enable_cutout
    self.cutout = cutout


    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()

  def format(self):
    if (type(self.api_keys) == str):
      self.api_keys = json_parse(self.api_keys)
    if (type(self.targets) == str):
      self.targets = json_parse(self.targets)
    if (type(self.inclusion_keywords) == str):
      self.inclusion_keywords = json_parse(self.inclusion_keywords)
    if (type(self.exclusion_keywords) == str):
      self.exclusion_keywords = json_parse(self.exclusion_keywords)
    return self


  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      name = self.name,
      type=self.type,
      api_keys = self.api_keys,
      targets = self.targets,
      inclusion_keywords = self.inclusion_keywords,
      exclusion_keywords = self.exclusion_keywords,
      period = str(self.period),
      start_time = self.start_time,
      end_time = self.end_time,
      schedule_interval = self.schedule_interval,
      schedule_time = self.schedule_time,
      metrics = self.metrics,
      rank_factors = self.rank_factors,
      status=self.status,
      enable_translation = self.enable_translation,
      target_langs = self.target_langs,
      enable_cutout = self.enable_cutout,
      cutout = self.cutout,
      created_at=self.created_at,
      updated_at=self.updated_at
    )

 