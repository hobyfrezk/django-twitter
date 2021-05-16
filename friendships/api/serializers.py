from rest_framework import serializers, exceptions
from friendships.models import Friendship
from accounts.api.serializers import UserSerializer

class FriendshipSerializerForCreateDelete(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise exceptions.ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )

    def delete(self):
        validated_data = [
            {**attrs, **kwargs} for attrs in self.validated_data
        ]

        deleted, _ = Friendship.objects.filter(
            from_user_id = validated_data['from_user_id'],
            to_user_id = validated_data['to_user_id'],
        ).delete()


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='from_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='to_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')
