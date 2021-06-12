from rest_framework import viewsets, permissions
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializer,
    TweetCreateSerializer,
    TweetSerializerWithComments
)
from tweets.models import Tweet
from utils.decorators import required_params


class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny(),]
        return [permissions.IsAuthenticated()]


    def retrieve(self, request, *args, **kwargs):

        tweet = self.get_object()

        return Response({
            'success': True,
            'tweet': TweetSerializerWithComments(tweet).data
        }, status=200)


    def create(self, request, *args, **kwargs):
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status = 400)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet=tweet)

        return Response(TweetSerializer(tweet).data, status=201)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        override list
        """

        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        serializer = TweetSerializer(tweets, many=True)

        return Response({
            'tweets': serializer.data
        })

