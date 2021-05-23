from functools import wraps
from django.contrib.auth.models import User
from rest_framework.response import Response


def validate_requested_user_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = User.objects.filter(id=kwargs["pk"])
        if not user:
            return Response(
                {
                    'success': False,
                    'message': 'Requested user does not exist',
                    'followers': [],
                }, status=400,
            )
        return func(*args, **kwargs)
    return wrapper
