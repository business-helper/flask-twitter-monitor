from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marketingBot import app
db = SQLAlchemy(app)

from marketingBot.helpers.common import json_parse

class Notification(db.Model):
  __tablename__ = 'notifications'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  text = db.Column(db.String(255), nullable=False)
  payload = db.Column(db.JSON)
  created_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, text, payload, **args):
    self.user_id = user_id
    self.text = text
    self.payload = payload
    self.created_at = datetime.utcnow()


  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      text = self.text,
      payload = self.payload,
      created_at=self.created_at,
    )

 