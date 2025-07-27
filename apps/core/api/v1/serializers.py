from rest_framework import serializers

from apps.core.models import BaseModel, Dropdown


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


class DropdownCustomRelatedField(serializers.RelatedField):
    def to_internal_value(self, value):
        return Dropdown.objects.filter(uuid=value).first().id


class DropdownSerializer(BaseSerializer):
    pid = DropdownCustomRelatedField(
        source="parent_id",
        queryset=Dropdown.objects.all(),
        write_only=True,
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
