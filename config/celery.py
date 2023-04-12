from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config', broker='redis://localhost:6379/0')

app.config_from_object(
    'django.conf:settings', namespace='CELERY'
)

app.conf.beat_schedule = {
    'update_task_missed': {
        'task': 'task.tasks.update_task_missed',
        'schedule': crontab(minute='*/2')
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('R-----------------------')
