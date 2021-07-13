# from flask_crontab import Crontab
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time

# crontab = Crontab(app)

# @crontab.job(minute = "1")
# def run_schedule_bots():
#   print('[Run Schedule Bot]')

def test_job():
    print('I am working...')


def run_as_thread():
  print('[Thread][Init]')
  threading.Thread(target = test_job).start()

  print('[Thread][Slept]')
  threading.Thread(target = test_job).start()


scheduler = BackgroundScheduler()
## remove all jobs
for job in scheduler.get_jobs():
  job.remove()

# jobs = scheduler.get_jobs()

job = scheduler.add_job(run_as_thread, 'interval', minutes=1, id='test_job_label')
# print('[Job]', job)
# print('[Job]', job.id)
# job_by_id = scheduler.get_job(job_id = 'test_job_label')
# print('[Jobs]', jobs, job_by_id)
scheduler.start()

