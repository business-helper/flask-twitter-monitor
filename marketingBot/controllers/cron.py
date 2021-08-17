# from flask_crontab import Crontab
from flask import jsonify
# ref: https://apscheduler.readthedocs.io/en/latest/modules/triggers/combining.html#module-apscheduler.triggers.combining
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import threading
from datetime import datetime
from pytz import timezone

from marketingBot.controllers.task_manager import run_bot_as_thread
from marketingBot.models.Notification import Notification, db
from marketingBot.models.Bot import Bot
from marketingBot import app

TEST_INTERVAL = 2
CRON_TEST = False

scheduler = BackgroundScheduler()

def convert_string_JST(str_datetime):
  try:
    dt = datetime.fromisoformat(str_datetime)
    dt.astimezone(timezone('Asia/Tokyo'))
    return dt
  except Exception as e:
    print(f"[Datetime][FormatError] {str_datetime} can't be converted!")
    return False

# bot: bot object
def schedule_bot_running(bot, reboot = False):
  if bot['schedule_interval'] == 0:
    print(f"[Schedule][Bot {bot['id']}] is unable to schedule")
    return False
  try:
    # trigger = CronTrigger(
    #   start_date=convert_string_JST(bot.schedule_time),
    # )
    trigger = IntervalTrigger(
      start_date=convert_string_JST(bot['schedule_time']),
      timezone=timezone('Asia/Tokyo'),
      days=int(bot['schedule_interval']) if not CRON_TEST else 0,
      minutes=TEST_INTERVAL if CRON_TEST else 0,
    )

    print(f"[Schedule][Bot]${bot['id']}")
    job = scheduler.add_job(run_bot_as_thread, trigger=trigger, id=str(bot['id']), replace_existing=True, args=[bot['id']])
    if not reboot:
      # notification of job added.
      notification = Notification(
        user_id=bot['user_id'],
        text=f"The Bot [{bot['name']}] has been scheduled!",
        payload={"type": "BOT_SCHEDULED", "bot": bot['id']},
      )
      db.session.add(notification)
      db.session.commit()
    return job
  except Exception as e:
    print(f"[Schedule][Bot {bot['id']}] Error:", str(e))
    raise e

# bot: bot object
def modify_bot_schedule(bot):
  if bot['schedule_interval'] == 0:
    print(f"[Schedule][Bot {bot['id']}] is unable to schedule")
    return False
  job = scheduler.get_job(job_id = str(bot['id']))
  try:
    job.remove()
  except Exception as e:
    print('[Modify Bot Schedule] Not found prev schedule')
    pass
  
  try:
    trigger = IntervalTrigger(
      start_date=convert_string_JST(bot['schedule_time']),
      timezone=timezone('Asia/Tokyo'),
      days=int(bot['schedule_interval']) if not CRON_TEST else 0,
      minutes=TEST_INTERVAL if CRON_TEST else 0,
    )
    # def run_bot(bot_id):
    #   print('[run_bot]', bot_id)
    #   run_bot_as_thread(bot_id)

    print(f"[Schedule][Bot][Modify] {bot['id']}")
    scheduler.add_job(run_bot_as_thread, trigger=trigger, id=str(bot['id']), replace_existing=True, args=[ bot['id'] ])

    # notification of job added.
    notification = Notification(
      user_id=bot['user_id'],
      text=f"The schedule for the Bot [{bot['name']}] has been reset!",
      payload={"type": "BOT_SCHEDULE_UPDATED", "bot": bot['id']},
    )
    db.session.add(notification)
    db.session.commit()
    return job
  except Exception as e:
    print(f"[Schedule][Bot {bot.id}] Error:", str(e))
    raise e

def initialize_schedule():
  # remove all jobs
  for job in scheduler.get_jobs():
    job.remove()
  
  one_time_bots = Bot.query.filter_by(type='ONE_TIME').all()
  print(f"[Found {len(one_time_bots)} One-Time Bots]")
  for bot in one_time_bots:
    bot_obj = bot.to_dict()
    schedule_bot_running(bot = bot_obj, reboot = True)

  print('[Booting System] Initialized schedule for one-time bots...')
  scheduler.start()

initialize_schedule()

def remove_bot_from_schedule(bot):
  try:
    job = scheduler.get_job(job_id = str(bot.id))
    job.remove()
    notification = Notification(
      text=f"A schedule for the Bot [{bot.name}] has been removed!",
      user_id = bot.user_id,
      payload={
        "type": "SCHEDULE_REMOVED",
        "bot": bot.id,
      },
    )
    db.session.add(notification)
    db.session.commit()
    return True
  except Exception as e:
    print(f"[Delete Job] Failed:", str(e))
    return False

# @test
def test_job():
    print('I am working...')
    # CronTrigger(start_date="2021-07-13", timezone="+0900")
    # # start_date: datetime
    # # days: int
    # IntervalTrigger()

# @test
def run_as_thread():
  print('[Thread][Init]')
  threading.Thread(target = test_job).start()

  print('[Thread][Slept]')
  threading.Thread(target = test_job).start()


# job = scheduler.add_job(run_as_thread, 'interval', minutes=1, id='test_job_label')
# jobs = scheduler.get_jobs()
# # print('[Job]', job)
# # print('[Job]', job.id)
# # job_by_id = scheduler.get_job(job_id = 'test_job_label')
# # print('[Jobs]', jobs, job_by_id)
# print('[Job Status]', job.id, job.name)
# scheduler.start()


@app.route('/list-jobs')
def list_jobs():
  jobs = scheduler.get_jobs()
  ids = list(map(lambda x: {"id": x.id}, jobs))
  return jsonify(ids)

@app.route('/run-as-thread/<id>')
def run_a_bot_as_thread(id):
  run_bot_as_thread(id)
  return jsonify({"status": True})

def get_next_run_time(bot_id):
  job = scheduler.get_job(job_id = str(bot_id))
  if not job:
    return False
  return str(job.next_run_time)
