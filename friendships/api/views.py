from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from friendships.api.serializers import FollowerSerializer, FriendshipSerializerForCreateDelete
from friendships.models import Friendship


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[permissions.AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=200,
        )

    @action(methods=['GET'], detail=True, permission_classes=[permissions.AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=200,
        )

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk):
        pk = int(pk)

        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            })

        serializer = FriendshipSerializerForCreateDelete(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=400)

        serializer.save()
        return Response({'success': True}, status=201)

    @action(methods=['POST'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, pk):
        pk = int(pk)
        if Friendship.objects.filter(from_user=pk, to_user=request.user).exists():
            return Response({
                'success': True,
                'duplicate': True,
            })

        serializer = FriendshipSerializerForCreateDelete(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        serializer.delete()

        return Response({
            'success': True,
            'deleted': deleted,
        })



