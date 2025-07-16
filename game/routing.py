from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/battle/', consumers.BattleConsumer.as_asgi()),
]