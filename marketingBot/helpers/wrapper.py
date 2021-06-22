from flask import session, redirect
from flask import flash
from functools import wraps

from marketingBot.helpers.common import validate_session

def session_required(f):
  @wraps(f)
  def _validate(*args, **kwargs):
    user = validate_session()
    if not user:
      flash('Please login again!')
      return redirect('/login')
    return f(user, *args, **kwargs)
  return _validate
