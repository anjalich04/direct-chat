import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        # 1. Handle Typing Status Broadcast
        if msg_type == 'typing':
            receiver_id = data.get('receiver_id')
            is_typing = data.get('is_typing', False)

            if receiver_id:
                await self.channel_layer.group_send(
                    f"user_{receiver_id}",
                    {
                        'type': 'typing_status',
                        'sender_id': self.user.id,
                        'sender_username': self.user.username,
                        'is_typing': is_typing
                    }
                )
            return

        # 2. Handle Direct Message Sending
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()

        if not receiver_id or not content:
            return

        msg_data = await self.save_message(self.user, receiver_id, content)

        if not msg_data:
            return

        # Broadcast message to recipient and sender
        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                'type': 'chat_message',
                'message': msg_data
            }
        )

        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {
                'type': 'chat_message',
                'message': msg_data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'is_typing': event['is_typing']
        }))

    async def messages_read(self, event):
        # Transmit read receipt event to sender WebSocket
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'reader_id': event['reader_id']
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver_id, content):
        try:
            receiver = User.objects.get(id=receiver_id)
            msg = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content
            )
            return {
                'id': msg.id,
                'sender_id': sender.id,
                'receiver_id': receiver.id,
                'sender_username': sender.username,
                'content': msg.content,
                'timestamp': msg.created_at.strftime('%b %d, %I:%M %p'),
                'is_read': False
            }
        except User.DoesNotExist:
            return None
