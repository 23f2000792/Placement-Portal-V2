import os

from celery import Celery
from celery.schedules import crontab


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://127.0.0.1:6379/1",
)


celery = Celery(
    "placement_portal",
    broker=REDIS_URL,
    backend=REDIS_URL,
)


celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)


celery.conf.beat_schedule = {
    "daily-deadline-reminders": {
        "task": "tasks.send_daily_deadline_reminders",
        "schedule": crontab(
            hour=9,
            minute=0,
        ),
    },
    "monthly-placement-report": {
        "task": "tasks.generate_scheduled_monthly_report",
        "schedule": crontab(
            day_of_month=1,
            hour=8,
            minute=0,
        ),
    },
}


if __name__ == "__main__":
    celery.start()