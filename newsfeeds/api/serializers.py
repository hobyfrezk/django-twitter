from rest_framework import serializers
from newsfeeds.models import Newsfeed
from tweets.api.serializers import TwitterSerializer

class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = Newsfeed
        fields = ('id', 'created_at', 'user', 'tweet')