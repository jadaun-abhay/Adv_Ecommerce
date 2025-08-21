from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from apps.core.models import BaseModel, Dropdown, User, UploadFile


# Write your serializers here


class BaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseModel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)

        super(BaseSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field in existing.difference(allowed):
                self.fields.pop(field)
        elif exclude is not None:
            not_allowed = set(exclude)
            for field in not_allowed:
                self.fields.pop(field)


@extend_schema_field(field=OpenApiTypes.UUID)
class DropdownCustomRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return Dropdown.objects.filter(id=value).first().uuid

    def to_internal_value(self, value):
        return Dropdown.objects.filter(uuid=value).first().id


class DropdownSerializer(BaseSerializer):
    pid = DropdownCustomRelatedField(
        source="parent_id",
        queryset=Dropdown.objects.all(),
        allow_null=True,
    )

    children = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Dropdown
        fields = "__all__"

    def get_children(self, instance):
        if "children" not in self.fields:
            return
        elif isinstance(instance, dict):
            return []
        else:
            queryset = instance.children.all()
            return DropdownSerializer(
                queryset,
                many=True,
                fields=self.fields,
            ).data

    def validate(self, data):
        parent_id = data.get("pid")
        if parent_id is not None:
            queryset = Dropdown.objects.filter(parent_id=parent_id)
            if queryset is None:
                raise serializers.ValidationError(
                    detail="parent does not exists", code="invalid parent"
                )
        return data

    def save(self):
        return Dropdown.objects.update_or_create(**self.validated_data)[0]


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def save(self):
        password = self.validated_data.get("password")
        user = User(**self.validated_data)
        user.set_password(password)
        user.save()
        return user


class UserCustomRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return User.objects.filter(id=value).first().uuid

    def to_internal_value(self, uuid):
        return User.objects.filter(uuid=uuid).first().id


class UploadFileSerializer(BaseSerializer):
    uid = UserCustomRelatedField(
        source="user_id",
        queryset=User.objects.all(),
        allow_null=True,
    )
    file = serializers.FileField()

    class Meta:
        model = UploadFile
        fields = "__all__"

    def save(self):
        instance = UploadFile.objects.create(**self.validated_data)
        return instance
