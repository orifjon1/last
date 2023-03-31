from django.urls import path
from .consumers import NotificationConsumer, ReviewConsumer


websocket_urlpatterns = [
    path('notification/', NotificationConsumer.as_asgi(), name='notification'),
    path('review/<int:task_id>/', ReviewConsumer.as_asgi(), name='review'),

]
