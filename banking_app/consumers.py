"""consumers.py"""
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class NotificationConsumer(WebsocketConsumer):
    """Notification function"""
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'notifications_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        sender = text_data_json['sender']
        amount = text_data_json['amount']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'notification',
                'sender': sender,
                'amount': amount
            }
        )

    # Receive message from room group
    def notification(self, event):
        """Receive notification"""
        sender = event['sender']
        amount = event['amount']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sender': sender,
            'amount': amount
        }))
