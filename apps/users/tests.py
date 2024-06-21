from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.factories import UserFactory, TeamFactory
from apps.users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.team = TeamFactory(tname="Test Team")
    
    def test_create_user(self):
        user = UserFactory(
            username="testuser",
            email="testuser@example.com",
            team=self.team,
            password="testpassword"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("testpassword"))
        
    def test_create_user_without_team(self):
        user = UserFactory(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("testpassword"))
        
    def test_create_adminuser(self):
        user = UserFactory(
            username="testadminuser",
            email="testadmuser@example.com",
            team=self.team,
            password="testadmpassword",
            is_admin=True
        )
        self.assertEqual(user.username, "testadminuser")
        self.assertEqual(user.email, "testadmuser@example.com")
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("testadmpassword"))
    
    def test_create_superuser(self):
        admin_user = UserFactory(
            username="adminuser",
            email="adminuser@example.com",
            team=self.team,
            password="adminpassword",
            is_admin=True,
            is_superuser=True,
            is_staff=True
        )
        self.assertEqual(admin_user.username, "adminuser")
        self.assertEqual(admin_user.email, "adminuser@example.com")
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.check_password("adminpassword"))
        

class UserViewsTest(APITestCase):
    def setUp(self):
        self.team = TeamFactory(tname="Test Team")
        self.user_data = {
            "username": "testuser2",
            "email": "testuser2@example.com",
            "password": "testpassword",
            "team": self.team.id
        }
        self.user = UserFactory(username="testuser", email="testuser@example.com", team=self.team, password="testpassword")
    
    def test_register_user(self):
        response = self.client.post(reverse('register'), self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='testuser2').exists())

    def test_register_user_without_email(self):
        user_data_without_email = {
            "username": "testuser3",
            "password": "testpassword",
            "team": self.team.id
        }
        response = self.client.post(reverse('register'), user_data_without_email, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn('email', response.data) 
    
    def test_login_user(self):
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessionid', response.cookies)
        
    def test_fail_login_user(self):
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Invalid Credentials'})
    
    def test_logout_user(self):
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        self.client.post(reverse('login'), login_data, format='json')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Logout successful'})