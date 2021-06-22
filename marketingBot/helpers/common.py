from flask import session
from marketingBot.models.User import User

def set_login_session(user):
  if not user:
    raise Exception('Invalid User!')
  session['login'] = True
  session['user_id'] = user.id
  session['user_email'] = user.email

def unset_login_session():
  session['login'] = None
  session['user_id'] = None
  session['user_email'] = None

def validate_session():
  if ('login' not in session) or not session['login']:
    unset_login_session()
    return False
  elif 'user_email' in session:
    user = User.query.filter_by(email=session['user_email']).first()
    if user:
      return user
    else:
      return False
  else:
    return False
