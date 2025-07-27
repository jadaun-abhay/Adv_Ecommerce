from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.v1.serializers import DropdownSerializer
from apps.core.models import Dropdown

# Write your views here


class BaseAV(APIView):
    pass


class DropdownAV(BaseAV):

    def get_instance(uuid):
        queryset = Dropdown.objects.filter(uuid=uuid)
        return queryset.first()

    def get(self, request):
        uuid = request.query_params.get("uuid", None)

        if uuid is None:
            queryset = Dropdown.objects.all()
            serializer = DropdownSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            instance = self.get_instance(uuid)
            serializer = DropdownSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = DropdownSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
