from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/stock/', consumers.StockConsumer.as_asgi()),
]