from django.test import TestCase, Client
from django.contrib.auth import get_user_model

class AdminLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'admin'
        self.password = 'admin'
        self.user = get_user_model().objects.create_superuser(
            username=self.username,
            email='admin@example.com',
            password=self.password
        )

    def test_admin_login_success(self):
        """Test that the superuser can log in to the Django Admin."""
        response = self.client.post('/django-admin/login/', {
            'username': self.username,
            'password': self.password,
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(response.context['user'].is_superuser)

    def test_wagtail_admin_login_success(self):
        """Test that the superuser can log in to the Wagtail Admin."""
        response = self.client.post('/admin/login/', {
            'username': self.username,
            'password': self.password,
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
