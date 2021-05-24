from tweets.models import Tweet
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from newsfeeds.services import NewsFeedService

class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny(),]
        return [permissions.IsAuthenticated()]

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

    def list(self, request, *args, **kwargs):
        """
        override list
        """
        if 'user_id' not in request.query_params:
            return Response('missing user id', status=400)

        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        serializer = TweetSerializer(tweets, many=True)

        return Response({
            'tweets': serializer.data
        })

