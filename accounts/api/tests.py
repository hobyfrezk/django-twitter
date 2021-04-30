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

    def _test_logged_in(self, expect_status):
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_logged_in'], expect_status)

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
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], test_account['username'])

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_signup_missing_parameters(self):
        # missing username
        response = self.client.post(SIGNUP_URL, {
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('username' in response.data['errors'], True)

        # missing email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('email' in response.data['errors'], True)

        # missing password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('password' in response.data['errors'], True)

    def test_username_occupied(self):
        self.createUser(
            username='linghu',
            email='linghu@jiuzhang.com',
            password='any password',
        )

        response = self.client.post(SIGNUP_URL, {
            'username': 'Linghu',
            'email': 'linghuchong@ninechpater.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)
        # print(response.data)
        self.assertEqual('username' in response.data['errors'], True)
        self.assertEqual('email' in response.data['errors'], False)

    def test_email_occupied(self):
        User.objects.create_user(username='linghu', email='linghu@jiuzhang.com')
        response = self.client.post(SIGNUP_URL, {
            'username': 'linghuchong',
            'email': 'Linghu@Jiuzhang.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('username' in response.data['errors'], False)
        self.assertEqual('email' in response.data['errors'], True)

    def test_signup_sucessed(self):
        self._test_logged_in(False)
        response = self.client.post(SIGNUP_URL, {
            'username': 'SOMEONE',
            'email': 'Someone@JIUZHANG.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        self.assertEqual(response.data['user']['email'], 'someone@jiuzhang.com')
        self._test_logged_in(True)

    def test_bad_login_request(self):
        # missing username
        data = {'password': 'linghu1234'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('username' in response.data['errors'], True)
        self.assertEqual('password' in response.data['errors'], False)

        # missing password
        data = {'username': 'linghuchong'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('username' in response.data['errors'], False)
        self.assertEqual('password' in response.data['errors'], True)

    def test_login_user_not_exist(self):
        data = {'username': 'linghuchong', 'password': 'linghu1234'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(response.data['errors']['username'][0].__str__(), 'User does not exist.')

class AccountLoginApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.linghu = self.create_user('linghu')

    def create_user(self, username):
        return User.objects.create_user(
            username=username,
            email=f'{username}@lintcode.com',
            password=f'{username}1234',
        )

    def _test_logged_in(self, data):
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertDictEqual(response.data['user'], {
            'id': self.linghu.id,
            'username': self.linghu.username,
            'email': self.linghu.email,
        })
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_success_logged_in(self):
        data = {'username': 'linghu', 'password': 'linghu1234'}
        self._test_logged_in(data)

    def test_case_insensitive(self):
        data = {'username': 'LINGHU', 'password': 'linghu1234'}
        self._test_logged_in(data)

    def test_get_method_not_allowed(self):
        data = {'username': 'linghu', 'password': 'linghu1234'}
        response = self.client.get(LOGIN_URL, data)
        self.assertEqual(response.status_code, 405)

    def test_username_password_mismatch(self):
        data = {'username': 'linghu', 'password': 'linghu123'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Username and password does not match.')

    def test_user_does_not_exist(self):
        data = {'username': 'linghuchong', 'password': 'linghu1234'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(response.data['errors']['username'][0].__str__(), 'User does not exist.')

    def test_bad_request(self):
        # missing username
        data = {'password': 'linghu1234'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('username' in response.data['errors'], True)
        self.assertEqual('password' in response.data['errors'], False)

        # missing password
        data = {'username': 'linghuchong'}
        response = self.client.post(LOGIN_URL, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('username' in response.data['errors'], False)
        self.assertEqual('password' in response.data['errors'], True)

