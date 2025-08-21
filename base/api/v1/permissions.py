from rest_framework.permissions import BasePermission

from base.api.v1.enums import RoleEnum
from apps.core.models import UserRole

# Write your permissions here


class APIAuthenticationPermission(BasePermission):
    def has_permission(self, request, view):
        authentication: dict | bool = getattr(view, "authentication", True)
        method: str = getattr(request, "method").lower()
        if not (
            authentication
            if isinstance(authentication, bool)
            else authentication.get(method, True)
        ):
            return True
        return request.user.is_authenticated


class APIAccessPermission(BasePermission):
    def has_permission(self, request, view):
        allowed_roles = getattr(
            view,
            "allowed_roles",
            [
                RoleEnum.ADMIN,
                RoleEnum.CUSTOMER,
            ],
        )
        if not allowed_roles:
            return True
        existing_roles = UserRole.objects.filter(user=request.user).values_list("id")
        if set(allowed_roles).intersection(set(existing_roles)):
            return True
        else:
            return False
