from rest_framework.views import APIView

from base.permissions import APIAuthenticationPermission, APIAccessPermission

# Write your views here


class BaseAV(APIView):
    authentication: dict | bool
    permission_classes: list = [
        APIAuthenticationPermission,
        APIAccessPermission,
    ]

    allowed_roles: list
