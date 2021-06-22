from flask import Flask, session, render_template, redirect, url_for, escape, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta

from marketingBot import app
from marketingBot.models.User import db, User



class CreateForm(FlaskForm):
    text = StringField('email', validators=[DataRequired()])
    text = StringField('password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
  print('[login]')
  form = CreateForm(request.form)
  if request.method == 'POST' and form.validate():
    from marketingBot.models.User import User
    user = User.authenticate(email=form.text.email, password=form.text.password)
    print('[User]')
    print(user)
    return print('hey')

  return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  print('[Register]')
  if request.method == 'POST':
    new_user = User(
      name=request.form['name'],
      email=request.form['email'],
      password=request.form['password'],
    )
    db.session.add(new_user)
    db.session.commit()
    return render_template('auth/login.html')
  return render_template('auth/register.html')
