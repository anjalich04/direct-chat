from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='Password123!'
        )

    def test_registration_success(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_duplicate_username(self):
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'other@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username already exists.")

    def test_registration_duplicate_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'otheruser',
            'email': 'existing@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email already exists.")

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match.")

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
