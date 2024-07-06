from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.organisations_url = reverse('organisations')
        self.user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }

    def test_register_user_successfully(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print("Validation errors:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], "John")
        self.assertEqual(response.data['data']['user']['lastName'], "Doe")
        self.assertEqual(response.data['data']['user']['email'], "john.doe@example.com")

    def test_login_user_successfully(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])

    def test_register_user_with_missing_fields(self):
        incomplete_data = {
            "firstName": "John",
            "email": "john.doe@example.com",
            "password": "password123"
        }
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_register_user_with_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')  # Register the first user

        duplicate_data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "john.doe@example.com",  # Duplicate email
            "password": "password123",
            "phone": "0987654321"
        }
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_access_protected_endpoint_with_token(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password'],
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['accessToken']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.organisations_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_access_protected_endpoint_without_token(self):
        response = self.client.get(self.organisations_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
