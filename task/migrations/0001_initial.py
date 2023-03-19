# Generated by Django 4.1.7 on 2023-03-14 05:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, max_length=200)),
                ('event', models.CharField(blank=True, max_length=100)),
                ('problem', models.TextField()),
                ('deadline', models.DateTimeField()),
                ('status', models.CharField(choices=[('missed', 'Missed'), ('doing', 'Doing'), ('finished', 'Done'), ('canceled', 'Canceled')], default='doing', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('financial_help', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('boss', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_tasks', to=settings.AUTH_USER_MODEL)),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accepted_tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='write your comment')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='task.taskreview')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_reviews', to='task.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]