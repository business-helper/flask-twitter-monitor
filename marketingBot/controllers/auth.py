from flask import Flask, session, render_template, redirect, url_for, escape, request
from datetime import datetime, timedelta

from marketingBot import app

@app.route('/login')
def login():
    return render_template('auth/login.html')


