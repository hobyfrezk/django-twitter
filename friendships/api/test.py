from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet
from friendships.models import Friendship

import pprint

class FriendshipApiTest(TestCase):
    @classmethod
    def get_followers_url(cls, pk):
        return f"/api/friendships/{pk}/followers/"

    @classmethod
    def get_followings_url(cls, pk):
        return f"/api/friendships/{pk}/followings/"

    @classmethod
    def follow_url(cls, pk):
        return f"/api/friendships/{pk}/follow/"

    def setUp(self):
        self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)


        self.user3 = self.create_user('user3', 'user3@jiuzhang.com')
        self.user3_client = APIClient()
        self.user3_client.force_authenticate(self.user3)


        self.user4 = self.create_user('user4', 'user4@jiuzhang.com')
        self.user4_client = APIClient()
        self.user4_client.force_authenticate(self.user4)


        self.user5 = self.create_user('user5', 'user5@jiuzhang.com')
        self.user5_client = APIClient()
        self.user5_client.force_authenticate(self.user5)

    def _add_friendship_relationships(self, type):
        # add friendship user1, user3, user4 --follow-> user2
        if type == "populate_followers":
            Friendship.objects.create(from_user=self.user1, to_user=self.user2)
            Friendship.objects.create(from_user=self.user3, to_user=self.user2)
            Friendship.objects.create(from_user=self.user4, to_user=self.user2)
            Friendship.objects.create(from_user=self.user5, to_user=self.user2)
        else:
            Friendship.objects.create(from_user=self.user2, to_user=self.user1)
            Friendship.objects.create(from_user=self.user2, to_user=self.user3)
            Friendship.objects.create(from_user=self.user2, to_user=self.user4)
            Friendship.objects.create(from_user=self.user2, to_user=self.user5)

    def test_follow(self):
        follow_user1_url = self.follow_url(pk=self.user1.id)

        # follow in anonymous -> 403
        response = self.anonymous_client.post(follow_user1_url)
        # pprint.pprint(response.__dict__)
        self.assertEqual(response.status_code, 403)

        # wrong http method -> 405
        response = self.user2_client.get(follow_user1_url)
        self.assertEqual(response.status_code, 405)

        # follow oneself -> 400
        response = self.user1_client.post(follow_user1_url)
        self.assertEqual(response.status_code, 400)

        # follow un-exist user -> 400
        follow_user_un_exist_url = self.follow_url(pk=6)
        response = self.user1_client.post(follow_user_un_exist_url)
        self.assertEqual(response.status_code, 400)

        # success follow -> 201; sql creation success
        count = Friendship.objects.count()
        response = self.user2_client.post(follow_user1_url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), 1 + count)

        # repeat follow -> 200
        response = self.user2_client.post(follow_user1_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['duplicate'], True)

    def test_get_follower(self):
        get_followers_user1_url = self.get_followers_url(pk=self.user1.id)
        get_followers_user2_url = self.get_followers_url(pk=self.user2.id)

        self._add_friendship_relationships("populate_followers")

        # fetch with wrong http method -> 405
        response = self.user1_client.post(get_followers_user1_url)
        self.assertEqual(response.status_code, 405)

        # fetch in anonymous -> 200
        response = self.anonymous_client.get(get_followers_user1_url)
        self.assertEqual(response.status_code, 200)

        # fetch case 0: fetch himself ->
        response = self.user1_client.get(get_followers_user1_url)
        self.assertEqual(response.status_code, 200)

        # fetch case 1: no followers user -> 200
        response = self.user2_client.get(get_followers_user1_url)
        self.assertEqual(response.status_code, 200)
        
        # fetch case 2: user with followers -> 200
        response = self.user1_client.get(get_followers_user2_url)
        self.assertEqual(response.status_code, 200)
        # pprint.pprint(response.data['followers'][0])
        self.assertEqual(len(response.data['followers']), 4)
        self.assertEqual(response.data['followers'][0]["user"]["username"], self.user5.username)

        # test if fans returned in decrease time order
        ts1 = response.data['followers'][0]["created_at"]
        ts2 = response.data['followers'][1]["created_at"]
        ts3 = response.data['followers'][2]["created_at"]
        ts4 = response.data['followers'][3]["created_at"]

        self.assertGreaterEqual(ts1, ts2)
        self.assertGreaterEqual(ts2, ts3)
        self.assertGreaterEqual(ts3, ts4)


    def test_get_following(self):
        get_following_user1_url = self.get_followings_url(pk=self.user1.id)
        get_following_user2_url = self.get_followings_url(pk=self.user2.id)

        self._add_friendship_relationships("populate_followings")

        # fetch with wrong http method -> 405
        response = self.user1_client.post(get_following_user1_url)
        self.assertEqual(response.status_code, 405)

        # fetch in anonymous -> 200
        response = self.anonymous_client.get(get_following_user1_url)
        self.assertEqual(response.status_code, 200)

        # fetch case 0: fetch himself -> 200
        response = self.user1_client.get(get_following_user1_url)
        self.assertEqual(response.status_code, 200)

        # fetch case 1: no following user -> 200
        response = self.user2_client.get(get_following_user1_url)
        self.assertEqual(response.status_code, 200)

        # fetch case 2: user with followings -> 200
        response = self.user1_client.get(get_following_user2_url)
        self.assertEqual(response.status_code, 200)

        # test if returned return followings in decreased time order
        ts1 = response.data['followings'][0]["created_at"]
        ts2 = response.data['followings'][1]["created_at"]
        ts3 = response.data['followings'][2]["created_at"]
        ts4 = response.data['followings'][3]["created_at"]

        self.assertGreaterEqual(ts1, ts2)
        self.assertGreaterEqual(ts2, ts3)
        self.assertGreaterEqual(ts3, ts4)
