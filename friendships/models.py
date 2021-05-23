from django.contrib.auth.models import User
from django.db import models


class Friendship(models.Model):
    # define friendship relationships,
    # from_user  --follow--> to_user
    #   ^ fans
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # Use case: list users you subscribed
            ('from_user_id', 'created_at'),
            # Use case: list your fans
            ('to_user_id', 'created_at'),
        )

        # add unique constraint
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return f'{self.from_user_id} followed {self.to_user_id}'
