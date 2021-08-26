from flask import Flask, session, render_template, redirect, url_for, escape, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask import flash

from marketingBot import db, app
from marketingBot.models.User import User
from marketingBot.helpers.common import set_login_session, unset_login_session, validate_session



class CreateForm(FlaskForm):
    text = StringField('email', validators=[DataRequired()])
    text = StringField('password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
  if validate_session():
    return redirect('/dashboard')
  if request.method == 'POST':
    user = User.authenticate(email=request.form['email'], password=request.form['password'])
    if user:
      set_login_session(user)
      return redirect("dashboard")
    else:
      flash('Invalid email address or password!')
    # return print('hey')

  return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    user_with_email = db.session.query(User).filter_by(email=request.form['email']).first()
    if user_with_email:
      flash("Email already exists with other account!")
      print(request.form)
      return render_template('auth/register.html', form=request.form)
    new_user = User(
      name=request.form['name'],
      email=request.form['email'],
      password=request.form['password'],
    )
    db.session.add(new_user)
    db.session.commit()
    return render_template('auth/login.html')
  return render_template('auth/register.html', form=None)

@app.route('/logout', methods=['GET'])
def logout_session():
  unset_login_session()
  return redirect('/login')
