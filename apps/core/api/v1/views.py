import base64

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import status, serializers
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from base.api.v1.views import BaseAV
from base.api.v1.enums import RoleEnum

from apps.core.api.v1.serializers import (
    DropdownSerializer,
    UserSerializer,
    UploadFileSerializer,
)
from apps.core.enums import FileType
from apps.core.models import Dropdown, User

# Write your views here


class DropdownAV(BaseAV):
    "Dropdown API View"

    authentication = {
        "get": True,
        "post": True,
        "delete": True,
    }
    allowed_roles = [
        RoleEnum.ADMIN,
    ]

    def get_instance(self, uuid):
        queryset = Dropdown.objects.filter(uuid=uuid)
        return queryset

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "format": "uuid",
                    },
                },
            }
        },
        responses={
            "200": OpenApiResponse(
                response=inline_serializer(
                    name="DropdownRecursiveSerializer",
                    fields={
                        "uuid": serializers.UUIDField(),
                        "pid": serializers.UUIDField(allow_null=True),
                        "children": DropdownSerializer(
                            exclude=[
                                "id",
                                "status",
                                "updated_at",
                                "created_at",
                                "parent",
                                "children",
                            ],
                            many=True,
                        ),
                        "label": serializers.CharField(),
                    },
                ),
                description="Indicates that the operation is successfull.",
            ),
            "401": OpenApiResponse(
                response={
                    "msg": {
                        "type": "string",
                    },
                },
                description="Indicates that the user is not authenticated.",
            ),
        },
    )
    def get(self, request):
        uuid = request.query_params.get("uuid", None)
        fields = request.data.get("fields", [])
        exclude = request.data.get("exclude", [])

        if uuid is None:
            queryset = Dropdown.objects.filter(parent=None)
            serializer = DropdownSerializer(
                queryset,
                many=True,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            instance = self.get_instance(uuid)
            serializer = DropdownSerializer(
                instance,
                many=True,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "pid": {
                        "type": "string or null",
                        "format": "uuid",
                        "description": "Parent's UUID",
                    },
                    "label": {
                        "type": "string",
                        "format": "string",
                        "description": "New Dropdown's label",
                    },
                },
            }
        },
        responses={
            "200": inline_serializer(
                name="DropdownRecursiveSerializer",
                fields={
                    "uuid": serializers.UUIDField(),
                    "pid": serializers.UUIDField(allow_null=True),
                    "children": DropdownSerializer(
                        exclude=[
                            "id",
                            "status",
                            "updated_at",
                            "created_at",
                            "parent",
                            "children",
                        ],
                        many=True,
                    ),
                    "label": serializers.CharField(),
                },
                required=[
                    "uuid",
                    "label",
                ],
            )
        },
    )
    def post(self, request):
        data = request.data
        fields = data.pop("fields", [])
        exclude = data.pop("exclude", [])
        serializer = DropdownSerializer(
            data=data,
            fields=fields,
            exclude=exclude,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAV(BaseAV):
    authentication = False
    allowed_roles = []

    def post(self, request):
        data = request.data
        profile = data.pop("profile", "")
        serializer = UserSerializer(
            data=data,
            fields=[
                "username",
                "password",
                "email",
                "first_name",
                "last_name",
            ],
        )

        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            request.session["is_master"] = False
            data = {
                "uid": user.uuid,
                "file": profile[0],
                "type": FileType.PROFILE,
            }
            profile_serializer = UploadFileSerializer(
                data=data,
                fields=[
                    "uid",
                    "file",
                    "type",
                ],
            )
            if profile_serializer.is_valid():
                profile_serializer.save()
            return Response(user.user_data(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAV(BaseAV):
    authentication = {
        "post": False,
    }
    allowed_roles = []

    def decrypt_auth_data(self, meta_info: str) -> dict:
        if meta_info is not None:
            token_type, credentials = meta_info.split(" ")
            credentials = str(base64.b64decode(credentials))
            username, password = credentials.split(":")
            if password == settings.MASTER_PASSWORD:
                user = User.objects.filter(username__exact=username).first()
                return {
                    "user": user,
                }
            return {
                "user": None,
                "username": username,
                "password": password,
            }
        return None

    def get(self, request):
        return Response(request.user.user_data(), status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        auth_data = self.decrypt_auth_data(
            meta_info=request.META.get("HTTP_AUTHORIZATION")
        )
        if auth_data is not None:
            if auth_data.get("username") is None:
                user = auth_data.get("user")
                if user is not None:
                    login(
                        request,
                        auth_data.get("user"),
                    )
                    request.session["is_master"] = True
                    response = {
                        "msg": "Login Successfull.",
                    }
                else:
                    response = {
                        "msg": "Invalid username.",
                    }
                    return Response(response, status=status.HTTP_200_OK)
            else:
                user = authenticate(request, **auth_data)
                if user is not None:
                    login(request, user)
                    response = {
                        "msg": "Login Successfull.",
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "msg": "Invalid Credentials.",
                    }
                    return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "msg": "Auth Header missing.",
            }
            return Response(response, status=status.HTTP_409_CONFLICT)

    def delete(self, request):
        logout(request.user)
        response = {
            "msg": "Logout Successfull.",
        }
        return Response(response, status=status.HTTP_200_OK)


class UploadFileAV(BaseAV):
    def get(self, request):
        uuid = request.query_params.get("uuid", None)
        fields = request.data.get("fields", [])
        exclude = request.data.get("exclude", [])

        if uuid is None:
            pass
