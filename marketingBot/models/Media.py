from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marketingBot import app
db = SQLAlchemy(app)

class Media(db.Model):
  __tablename__ = 'media'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, nullable = False)
  origin_name = db.Column(db.String(100), nullable = False)
  path = db.Column(db.String(255), nullable = False)
  media_id = db.Column(db.String(30), nullable = False)
  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, user_id, origin_name, path, media_id, **args):
    self.user_id = user_id
    self.origin_name = origin_name
    self.path = path
    self.media_id = media_id

    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()

  def to_dict(self):
    return dict(
      id=self.id,
      user_id = self.user_id,
      origin_name = self.origin_name,
      path = self.path,
      media_id = self.media_id,
      created_at=self.created_at,
      updated_at=self.updated_at
    )

 