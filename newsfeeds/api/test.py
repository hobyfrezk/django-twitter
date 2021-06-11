from rest_framework.test import APIClient
from testing.testcases import TestCase

import pprint

NEWSFEEDS_URL = "/api/newsfeeds/"
TWEET_CREATE_API = '/api/tweets/'

def follow_url(pk):
    return f"/api/friendships/{pk}/follow/"

class NewsFeed(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list(self):
        # anonymous account can not get newsfeed
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        # wrong http method -> 405
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        # user2 fetch newsfeed -> 200, empty newsfeed
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)

        # user2 follow user 1
        follow_user1_url = follow_url(pk=self.user1.id)
        response = self.user2_client.post(follow_user1_url)
        self.assertEqual(response.status_code, 201)

        # user1 send new tweet
        tweet_content_1 = "user1 1st tweet"
        response = self.user1_client.post(TWEET_CREATE_API,
                                          {'content': tweet_content_1})
        self.assertEqual(response.status_code, 201)

        # user2 get newsfeed
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        # print(response.data)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['content'],
                         tweet_content_1)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['user']['id'],
                         self.user1.id)

        # user1 send new tweet again
        new_tweet_contents = [f"user1 {num} tweet" for num in range(5)]
        for tweet_content in new_tweet_contents:
            response = self.user1_client.post(TWEET_CREATE_API,
                                              {'content': tweet_content})
            self.assertEqual(response.status_code, 201)

        # user2 get newsfeed in time decreasing order
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), len(new_tweet_contents)+1)
        time_stamps = [x['created_at'] for x in response.data["newsfeeds"]]
        for i in range(len(time_stamps)-1):
            self.assertGreaterEqual(time_stamps[i], time_stamps[i+1])


