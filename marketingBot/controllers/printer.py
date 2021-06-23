# -*- coding: utf-8 -*-
from marketingBot import app
from flask import render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CreateForm(FlaskForm):
    text = StringField('name', validators=[DataRequired()])


@app.route('/')
def start():
  return redirect('/login')
  # return render_template('printer/index.html')


@app.route('/print', methods=['GET', 'POST'])
def printer():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        from marketingBot.models.Printer import Printer
        printer = Printer()
        printer.show_string(form.text.data)
        return render_template('printer/index.html')
    return render_template('printer/print.html', form=form)
