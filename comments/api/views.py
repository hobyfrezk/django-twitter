from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.api.serializers import CommentSerializer, CommentSerializerForCreate, CommentSerializerForUpdate
from comments.models import Comment
from utils.decorators import required_params

class CommentViewSet(viewsets.GenericViewSet,
                     viewsets.mixins.ListModelMixin,
                     viewsets.mixins.CreateModelMixin,
                     viewsets.mixins.UpdateModelMixin,
                     viewsets.mixins.DestroyModelMixin):

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id', )

    def get_permissions(self):

        if self.action == "create":
            return [IsAuthenticated()]

        if self.action in ["update", "destroy"]:
            return [IsAuthenticated(), IsObjectOwner()]

        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).prefetch_related('user')

        serializer = CommentSerializer(comments, many=True)

        return Response({
            'comments': serializer.data
        })

    def create(self, request, *args, **kwargs):
        data = {
            "user_id": request.user.id,
            "tweet_id": request.data.get('tweet_id'),
            "content": request.data.get('content'),
        }

        serializer = CommentSerializerForCreate(data=data)

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)

        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=201
        )

    def update(self, request, *args, **kwargs):
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'error': serializer.errors,
            }, status=400)

        comment = serializer.save()
        return Response({
            'success': True,
            'comment': CommentSerializer(comment).data,
        }, status=200)

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
        }, status=200)

