from functools import wraps
from rest_framework.response import Response

def require_admin_authentication(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        admin_username = request.headers.get("username")
        if not admin_username:
            return Response({
                "status": "false",
                "message": "Admin authentication failed",
                "statusCode": "001",
            }, status=400)
        return view_func(self, request, *args, **kwargs)
    
    return wrapper
