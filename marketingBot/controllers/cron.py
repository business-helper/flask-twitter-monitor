# from flask_crontab import Crontab
from marketingBot import app
from apscheduler.schedulers.background import BackgroundScheduler

# crontab = Crontab(app)

# @crontab.job(minute = "1")
# def run_schedule_bots():
#   print('[Run Schedule Bot]')

def test_job():
    print('I am working...')

scheduler = BackgroundScheduler()
job = scheduler.add_job(test_job, 'interval', minutes=1)
scheduler.start()

