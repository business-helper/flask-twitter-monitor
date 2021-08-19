from datetime import datetime
from marketingBot import db

class AppKey(db.Model):
  __tablename__ = 'api_keys'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable=False)
  name = db.Column(db.String(50), nullable=False)
  consumer_key = db.Column(db.String(100), nullable=False)
  consumer_secret = db.Column(db.String(100), nullable=False)
  access_token = db.Column(db.String(100), nullable=False)
  access_token_secret = db.Column(db.String(100), nullable=False)
  bearer_token = db.Column(db.String(255), nullable=False)
  valid = db.Column(db.Boolean, default=1)

  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, name, consumer_key, consumer_secret, access_token, access_token_secret, bearer_token, valid, **args):
    self.user_id = user_id
    self.name = name
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token = access_token
    self.access_token_secret = access_token_secret
    self.bearer_token = bearer_token
    self.valid = valid

    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()

  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      name = self.name,
      consumer_key = self.consumer_key,
      consumer_secret = self.consumer_secret,
      access_token = self.access_token,
      access_token_secret = self.access_token_secret,
      bearer_token = self.bearer_token,
      valid=self.valid,
      created_at=self.created_at,
      updated_at=self.updated_at
    )

 