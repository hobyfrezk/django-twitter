from friendships.services import FriendshipService

class NewsFeedService:

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        # add tweet's owner to the newsfeeds
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))

        Newsfeeds.objects.bulk_create(newsfeeds)
