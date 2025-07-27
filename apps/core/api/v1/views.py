from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.v1.serializers import DropdownSerializer
from apps.core.models import Dropdown

# Write your views here


class BaseAV(APIView):
    pass


class DropdownAV(BaseAV):

    def get_instance(self, uuid):
        queryset = Dropdown.objects.filter(uuid=uuid)
        return queryset

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
