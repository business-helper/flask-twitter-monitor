from flask_crontab import Crontab
from marketingBot import app

crontab = Crontab(app)

@crontab.job(minute = "1")
def run_schedule_bots():
  print('[Run Schedule Bot]')



