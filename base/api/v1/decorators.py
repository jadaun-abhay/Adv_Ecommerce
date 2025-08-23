from typing import Any

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    inline_serializer,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from rest_framework import serializers
from rest_framework.settings import api_settings

from base.api.v1.constants import SUCCESS_RESPONSES
from base.api.v1.types import CustomErrorResponseType

# Write your decorators here


def extend_response_schema(type: Any | None):
    def wrapper_extend_response_schema(func):
        method = getattr(func, "__name__")
        success_response_code = SUCCESS_RESPONSES.get(method)
        return extend_schema(
            responses={
                success_response_code: OpenApiResponse(
                    response=type,
                    description="Indicates that the operation is successfull.",
                ),
            }
        )(func)

    return wrapper_extend_response_schema


def extend_base_schema(cls, func):
    method = getattr(func, "__name__")
    extend_schema_params = {}

    authentication = getattr(cls, "authentication", True)
    responses = {}

    if (
        authentication
        if isinstance(authentication, bool)
        else authentication.get(method, True)
    ):
        responses = {
            "400": OpenApiResponse(
                response=inline_serializer(
                    name="CustomErrorSerializer",
                    fields={
                        "msg": serializers.StringRelatedField(),
                    },
                ),
                description="Raised when there is any custom error.",
            ),
            "401": OpenApiResponse(
                response=inline_serializer(
                    name="AuthenticationErrorSerializer",
                    fields={
                        "msg": serializers.StringRelatedField(),
                    },
                ),
                description="Raised when the user is not authenticated.",
            ),
            "403": OpenApiResponse(
                response=inline_serializer(
                    name="AuthorizationErrorSerializer".format(method.upper()),
                    fields={
                        "msg": serializers.StringRelatedField(),
                    },
                ),
                description="Raised when the user is not authorised to view the resource.",
            ),
        }
    else:
        extend_schema_params["auth"] = []

    BaseSchema = (
        # explicit manually set schema or previous view annotation
        getattr(func, "schema", None)
        # previously set schema with @extend_schema on views methods
        or getattr(func, "kwargs", {}).get("schema", None)
        # the default
        or api_settings.DEFAULT_SCHEMA_CLASS
    )

    class ExtendedSchema(BaseSchema):
        def get_response_serializers(self):
            _responses = super().get_response_serializers() or {}
            _responses.update(responses)
            return _responses

    if not hasattr(func, "kwargs"):
        func.kwargs = {}
    # this simulates what @action is actually doing. somewhere along the line in this process
    # the schema is picked up from kwargs and used. it's involved my dear friends.
    # use class instead of instance due to descriptor weakref reverse collisions
    func.kwargs["schema"] = ExtendedSchema

    return extend_schema(**extend_schema_params)(func)
