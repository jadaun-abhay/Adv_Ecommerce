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
        authentication: dict | bool = getattr(view, "authentication", True)
        method: str = getattr(request, "method").lower()
        if not (
            authentication
            if isinstance(authentication, bool)
            else authentication.get(method, True)
        ):
            return True

        allowed_roles = getattr(
            view,
            "allowed_roles",
            ["ADMIN"],
        )

        authorized_roles: list = []
        if not allowed_roles:
            return request.user.is_authenticated
        existing_roles = list(
            UserRole.objects.filter(user=request.user).values_list("uuid")
        )

        for each in allowed_roles:
            roles = list(
                UserRole.objects.filter(user=request.user, role__role=each).values_list(
                    "uuid"
                )
            )
            authorized_roles.extend(roles)
        if request.session["is_master"]:
            return True
        elif set(authorized_roles).intersection(set(existing_roles)):
            if request.session["is_master"]:
                return True
            return request.user.is_authenticated
        else:
            return False
