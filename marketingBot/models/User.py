from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from marketingBot import app
db = SQLAlchemy(app)

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  email = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  socket_id = db.Column(db.String(100), nullable=True)
  created_at = db.Column(db.String(30), nullable=True)
  updated_at = db.Column(db.String(30), nullable=True)


  def __init__(self, email, password, name, **args):
    self.name = name
    self.email = email
    self.password = generate_password_hash(password).decode('utf-8')
    self.created_at = datetime.utcnow()
    self.updated_at = datetime.utcnow()
  
  @classmethod
  def authenticate(cls, **kwargs):
    email = kwargs.get('email')
    password = kwargs.get('password')

    if not email or not password:
      return None
   
    user = cls.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
      return None
    return user


  def to_dict(self):
    return dict(
      id = self.id,
      email = self.email,
      name = self.name,
      socket_id = self.socket_id,
      created_at = self.created_at,
      updated_at = self.updated_at
    )

 