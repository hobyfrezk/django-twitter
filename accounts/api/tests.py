from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):

    @staticmethod
    def createUser(username, email, password):
        return User.objects.create_user(username, email, password)

    def setUp(self):
        # will be called every time test function is running
        self.client = APIClient()
        self.test_data = {
            'username': 'admin_account',
            'email': 'admin@test.com',
            'password': 'admin_test_pwd'
        }
        self.user = self.createUser(
            username=self.test_data['username'],
            email=self.test_data['email'],
            password=self.test_data['password'],
        )

    def test_login(self):
        """
        test login procedure
        - wrong method?
        - wrong password?
        - default logged status is un-logged?
        - logged with correct user data
        """

        response = self.client.get(LOGIN_URL, {
            'username': self.test_data['username'],
            'password': self.test_data['password'],
        })
        self.assertEqual(response.status_code, 405)

        response = self.client.post(LOGIN_URL, {
            'username': self.test_data['username'],
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        response = self.client.post(LOGIN_URL, {
            'username': self.test_data['username'],
            'password': self.test_data['password'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['username'], self.test_data['username'])
        self.assertEqual(response.data['user']['email'], self.test_data['email'])

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # log in default user before test logout
        self.client.post(LOGIN_URL, {
            'username': self.test_data['username'],
            'password': self.test_data['password'],
        })

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):

        test_account = {
            'username': 'test_account',
            'email': 'test@test.com',
            'password': 'test_pwd'
        }

        response = self.client.get(SIGNUP_URL, test_account)
        self.assertEqual(response.status_code, 405)

        response = self.client.post(SIGNUP_URL, {
            'username': test_account['username'],
            'email': 'not a correct email',
            'password': test_account['password']
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': test_account['username'],
            'email': test_account['email'],
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': test_account['email'],
            'password': test_account['password'],
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, test_account)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], test_account['username'])

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)