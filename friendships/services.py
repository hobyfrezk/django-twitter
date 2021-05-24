from friendships.models import Friendship
from django.contrib.auth.models import User

class FriendshipService:

    @classmethod
    def get_followers(cls, user):
        # get followers of a user
        # 2 way to avoid N+1 Queries
        # 1st method
        # friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 2nd method
        friendships = Friendship.objects.filter(to_user=user)
        follower_ids = [friendship.from_user_id for friendship in friendships]

        return User.objects.filter(id__in=follower_ids)
