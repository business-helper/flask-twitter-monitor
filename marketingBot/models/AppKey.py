from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from marketingBot import app
db = SQLAlchemy(app)

class AppKey(db.Model):
  __tablename__ = 'api_keys'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(50), nullable=False)
  consumer_key = db.Column(db.String(100), nullable=False)
  consumer_secret = db.Column(db.String(100), nullable=False)
  access_token = db.Column(db.String(100), nullable=False)
  access_token_secret = db.Column(db.String(100), nullable=False)
  valid = db.Column(db.Boolean, default=1)

  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, name, consumer_key, consumer_secret, access_token, access_token_secret, valid, **args):
    self.user_id = user_id
    self.name = name
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token = access_token
    self.access_token_secret = access_token_secret
    self.valid = valid

    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()

  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      consumer_key = self.consumer_key,
      consumer_secret = self.consumer_secret,
      access_token = self.access_token,
      access_token_secret = self.access_token_secret,
      created_at=self.created_at,
      updated_at=self.updated_at
    )

 