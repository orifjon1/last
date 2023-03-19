from users.models import CustomUser
from django.db import models
from datetime import datetime


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


class TaskReview(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_reviews')
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='user_reviews')
    content = models.TextField(help_text='write your comment')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

