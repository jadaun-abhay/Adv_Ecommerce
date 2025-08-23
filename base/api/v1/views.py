from rest_framework.views import APIView

from base.api.v1.permissions import APIAuthenticationPermission, APIAccessPermission
from base.api.v1.decorators import extend_base_schema

# Write your views here


class BaseAV(APIView):
    authentication: dict | bool
    permission_classes: list = [
        APIAuthenticationPermission,
        APIAccessPermission,
    ]

    allowed_roles: list

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for method in cls.http_method_names:
            useful = getattr(cls, method, None)
            if useful is not None and callable(useful):
                schema = extend_base_schema(cls, useful)
                setattr(cls, method, schema)
