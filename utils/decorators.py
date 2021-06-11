from functools import wraps
from django.contrib.auth.models import User
from rest_framework.response import Response

def required_params(request_attr='query_params', params=None):
    if params is None:
        params = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ', '.join(missing_params)
                return Response(
                    {
                        'success': False,
                        'message': f'missing {params_str} in request',
                    }, status=400,
                )
            return view_func(instance, request, *args, **kwargs)
        return wrapper_view

    return decorator