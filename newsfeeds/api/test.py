from rest_framework.test import APIClient
from testing.testcases import TestCase

NEWSFEEDS_URL = "localhost/api/newsfeeds"

class NewsFeed(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()


    def test_list(self):
        response = self.anonymous_client.get()