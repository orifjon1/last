from django.dispatch import receiver

from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from django.db import models
from datetime import datetime
from django.db.models.signals import post_save


class Task(models.Model):
    STATUS_CHOICES = (
        ('missed', 'Missed'),
        ('doing', 'Doing'),
        ('finished', 'Done'),
        ('canceled', 'Canceled'),
    )

    reason = models.CharField(max_length=200, blank=True)
    event = models.CharField(max_length=100, blank=True)
    problem = models.TextField()
    deadline = models.DateTimeField()
    boss = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='given_tasks')
    worker = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='accepted_tasks')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='doing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    financial_help = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.boss} gave a task to {self.worker}"

    @property
    def all_days(self):
        days = (self.deadline.date() - self.created_at.date()).days
        return days

    @property
    def remain_days(self):
        remain = (self.deadline.date() - datetime.now().date()).days
        return remain


@database_sync_to_async
@receiver(post_save, sender=Task)
def notification(sender, instance, created, **kwargs):
    worker = instance.worker
    if created and worker:
        channel_layer = get_channel_layer()
        message = {
            'type': 'notify.user',
            'message': f"{worker.first_name}, {instance.boss.first_name} sizga yangi topshiriq yubordi!"
        }
        channel_name = f"user_{worker.username}"
        async_to_sync(channel_layer.group_send)(channel_name, message)


class TaskUpdateTimes(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updated_times')
    updated_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='updated_tasks')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created.date()}'


@receiver(post_save, sender=Task)
def create_update_time(sender, instance, created, **kwargs):
    if not created:
        TaskUpdateTimes.objects.create(
            task=instance, updated_by=instance.boss
        )


class TaskReview(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_reviews')
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='user_reviews')
    content = models.TextField(help_text='write your comment')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

