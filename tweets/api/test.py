from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet


TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTest(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.tweets1 = [
            self.create_tweet(user=self.user1, content=None)
            for _ in range(3)
        ]

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.tweets2 = [
            self.create_tweet(user=self.user2, content=None)
            for _ in range(2)
        ]

    def test_list_api(self):
        # test get method w/o user_id in param
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # normal request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)

        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 2)

        # test returned tweets order
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # only logged in user can create
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # content can not be empty
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)

        # content too short
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # content too long
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0'*256
        })
        self.assertEqual(response.status_code, 400)

        # normal case
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello world, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # tweet with id=-1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # check if comments were retrieved along with tweet
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweet']['comments']), 0)

        self.create_comment(self.user2, tweet, 'holly s***')
        self.create_comment(self.user1, tweet, 'hmm...')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['tweet']['comments']), 2)