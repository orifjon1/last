from django.db.models import Q

from config.celery import app
from task.models import Task


@app.task()
def update_task_missed():
    tasks = Task.objects.filter(Q(deadline__date__lt=0) and Q(status='doing')).exclude(status='missed')
    if tasks:
        for task in tasks:
            task.status = 'missed'
            task.save()

