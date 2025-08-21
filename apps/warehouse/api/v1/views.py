import json

from rest_framework.response import Response
from rest_framework import status

from apps.core.api.v1.views import BaseAV
from apps.core.enums import Status

from apps.warehouse.api.v1.serializers import CategorySerializer, ProductSerializer
from apps.warehouse.models import Category, Product

from base.api.v1.enums import RoleEnum


# Write your views here


class CategoryAV(BaseAV):
    authentication = {
        "get": True,
        "post": True,
        "put": True,
        "delete": True,
    }

    allowed_roles = [
        RoleEnum.ADMIN,
        RoleEnum.CUSTOMER,
    ]

    def get_instance(self, uuid):
        queryset = Category.objects.filter(uuid=uuid)
        return queryset

    def get(self, request):
        uuid = request.query_params.get("uuid", None)
        fields = request.data.get("fields", [])
        exclude = request.data.get("exclude", [])

        if uuid is None:
            queryset = Category.objects.filter(parent=None)
            serializer = CategorySerializer(
                queryset,
                many=True,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            instance = self.get_instance(uuid)
            serializer = CategorySerializer(
                instance,
                many=True,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        fields = data.get("fields", [])
        exclude = data.get("exclude", [])

        serializer = CategorySerializer(
            data=data,
            fields=fields,
            exclude=exclude,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        data = request.data
        fields = data.get("fields", [])
        exclude = data.get("exclude", [])

        uuid = data.get("uuid", None)
        instance = Category.objects.filter(uuid=uuid).first()

        serializer = CategorySerializer(
            instance,
            data,
            context={
                "method": request.method,
            },
            fields=fields,
            exclude=exclude,
        )

        if serializer.is_valid():
            instance = serializer.save()
            serializer = CategorySerializer(
                instance,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data

        uuid = data.get("uuid", None)
        instance = Category.objects.filter(uuid=uuid).first()
        if instance is None:
            response = {
                "message": "No records exists",
            }
            return Response(response, status=status.HTTP_409_CONFLICT)

        serializer = CategorySerializer(
            instance,
            {
                "uuid": uuid,
                "status": Status.DELETED,
            },
        )

        if serializer.is_valid():
            instance = serializer.save()
            response = {
                "message": "Record is deleted successfully.",
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_200_OK)


class ProductAV(BaseAV):
    def get_instance(self, uuid):
        queryset = Product.objects.filter(category__uuid=uuid)
        return queryset

    def get(self, request):
        uuid = request.query_params.get("uuid")
        fields = request.data.get("fields", [])
        exclude = request.data.get("exclude", [])

        if uuid is None:
            response = {
                "message": "category uuid is not provided",
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            instance = self.get_instance(uuid)
            serializer = ProductSerializer(
                instance,
                many=True,
                fields=fields,
                exclude=exclude,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        fields = json.loads(data.get("fields", "[]"))
        exclude = json.loads(data.get("exclude", "[]"))
        file = data.get("image")

        serializer = ProductSerializer(
            data=data,
            fields=fields,
            exclude=exclude,
        )
        if serializer.is_valid():
            instance = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
