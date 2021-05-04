from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)

from accounts.api.serializers import UserSerializer
from accounts.api.serializers import SignupSerializer, LoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AccountViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to sign up, login, logout and check login status.
    """

    serializer_class = SignupSerializer
    permissions_classes = (permissions.AllowAny,)

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        Signup with username, email, password
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)

        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)

        username = serializer.validated_data['username'].lower()
        password = serializer.validated_data['password']

        # check user exists
        if not User.objects.filter(username=username):
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": {
                    "username": ["User does not exist."]
                }
            }, status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        django_login(request, user)

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return Response({
            "success": True,
            "user": user_data
        })

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        # check login status
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data

        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        # logout
        django_logout(request)
        return Response({"success": True})
