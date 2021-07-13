# from flask_crontab import Crontab
from flask import jsonify
# ref: https://apscheduler.readthedocs.io/en/latest/modules/triggers/combining.html#module-apscheduler.triggers.combining
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import threading
from datetime import datetime
from pytz import timezone
import time
from marketingBot.controllers.task_manager import run_bot_as_thread
from marketingBot import app

scheduler = BackgroundScheduler()

def test_job():
    print('I am working...')
    # CronTrigger(start_date="2021-07-13", timezone="+0900")
    # # start_date: datetime
    # # days: int
    # IntervalTrigger()


def run_as_thread():
  print('[Thread][Init]')
  threading.Thread(target = test_job).start()

  print('[Thread][Slept]')
  threading.Thread(target = test_job).start()

def schedule_bot_running(bot):
  if bot.schedule_interval == 0:
    print(f"[Schedule][Bot {bot.id}] is unable to schdule")
    return False
  try:
    trigger = CronTrigger(
      start_date=convert_strignt_JST(bot.schedule_time),
      timezone=timezone('Asia/Tokyo'),
      day=bot.schedule_interval,
    )
    def run_bot():
      run_bot_as_thread(bot.id)
    job = scheduler.add_job(run_bot, trigger=trigger, id=bot.id)
    return job
  except Exception as e:
    print(f"[Schedule][Bot {bot.id}] Error:", str(e))
    pass

def convert_strignt_JST(str_datetime):
  try:
    dt = datetime.fromisoformat(str_datetime)
    dt.astimezone(timezone('Asia/Tokyo'))
    return dt
  except Exception as e:
    print(f"[Datetime][FormatError] {str_datetime} can't be converted!")
    return False



## remove all jobs
for job in scheduler.get_jobs():
  job.remove()


job = scheduler.add_job(run_as_thread, 'interval', minutes=1, id='test_job_label')
jobs = scheduler.get_jobs()
# print('[Job]', job)
# print('[Job]', job.id)
# job_by_id = scheduler.get_job(job_id = 'test_job_label')
# print('[Jobs]', jobs, job_by_id)
print('[Job Status]', job.id, job.name)
scheduler.start()


@app.route('/list-jobs')
def list_jobs():
  jobs = scheduler.get_jobs()
  ids = list(map(lambda x: x.id, jobs))
  return jsonify(ids)

