import time
from django.utils import timezone
from task.models import Task


def missed():
    tasks = Task.objects.filter(is_active=True)
    if tasks is None:
        tasks = None
    else:
        for t in tasks:
            if t.remain_days() < 2:
                t.status = 'missed'
                t.save()
                print("ok, mission is done! ")


# while True:
#     missed()
#     time.sleep(2 * 60)
