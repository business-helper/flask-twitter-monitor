from datetime import datetime
from marketingBot import db

from marketingBot.helpers.common import json_parse

class Notification(db.Model):
  __tablename__ = 'notifications'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, nullable=False, default = 0)
  bot_id = db.Column(db.Integer, nullable=False, default = 0)
  text = db.Column(db.Text, nullable=False)
  payload = db.Column(db.JSON)
  created_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, text, payload, bot_id = 0, **args):
    self.user_id = user_id
    self.bot_id = bot_id
    self.text = text
    self.payload = payload
    self.created_at = datetime.utcnow()


  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      bot_id = self.bot_id,
      text = self.text,
      payload = self.payload,
      created_at=self.created_at,
    )

 