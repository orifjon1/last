from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from task.models import TaskReview, Task
from users.models import CustomUser


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["user"].username
        self.group_name = f'user_{self.username}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)

    async def notify_user(self, event):
        message = event['message']
        await self.send(
            text_data=json.dumps(
                {
                    'message': message
                }
            )
        )


class ReviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        task_id = self.scope['url_rout']['kwargs']['task_id']
        self.group_name = f'chat_{task_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data)
        message = text_data['message']
        username = self.scope['user'].username
        task_id = text_data['task_id']

        await self.save_content(
            message, username, task_id
        )
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'review_message',
                'message': message,
                'username': username
            }
        )

    async def review_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @database_sync_to_async
    async def save_content(self, message, username, task_id):
        task = Task.objects.get(id=task_id)
        user = CustomUser.objects.get(username=username)
        TaskReview.objects.create(task=task, user=user, content=message)
