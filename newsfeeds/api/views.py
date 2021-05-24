from rest_framework import viewsets, permissions
from newsfeeds.models import NewsFeed
from rest_framework.response import Response

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        newsfeeds = self.get_queryset()
        serializer = NewsFeedSerializer(newsfeeds, many=True)
        return Response({
            'newsfeeds': serializer.data,
        }, status=200)
