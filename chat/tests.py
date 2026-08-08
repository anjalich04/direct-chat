import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Message

class ChatTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='Password123!')
        self.msg = Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello User 2')

    def test_message_creation(self):
        self.assertEqual(str(self.msg), "user1 -> user2: Hello User 2")
        self.assertFalse(self.msg.is_read)

    def test_get_users_list_api(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('api_users'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('users', data)
        self.assertEqual(len(data['users']), 1)
        self.assertEqual(data['users'][0]['username'], 'user2')

    def test_get_chat_history_api(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('get_chat_history', kwargs={'user_id': self.user2.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('messages', data)
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], 'Hello User 2')

    def test_mark_messages_as_read_api(self):
        self.client.force_login(self.user2)
        response = self.client.patch(reverse('api_mark_read', kwargs={'other_user_id': self.user1.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_read)

    def test_send_message_api(self):
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('send_message'),
            data=json.dumps({'receiver_id': self.user2.id, 'content': 'API sent message'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Message.objects.filter(content='API sent message').exists())
