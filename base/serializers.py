from rest_framework import serializers

from apps.core.models import BaseModel

# Write your serializers here


class BaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseModel
