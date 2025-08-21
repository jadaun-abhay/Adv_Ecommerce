from rest_framework import serializers

from apps.core.api.v1.serializers import BaseSerializer
from apps.core.models import UploadFile
from apps.warehouse.models import Category, Product

# Write your serializers here


class CategoryCustomRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return Category.objects.filter(id=value).first().uuid

    def to_internal_value(self, value):
        instance = Category.objects.filter(uuid=value).first()
        if instance is None:
            raise serializers.ValidationError(
                detail="Parent does not exists",
                code="invalid parent",
            )
        return instance.id


class CategorySerializer(BaseSerializer):
    pid = CategoryCustomRelatedField(
        source="parent_id",
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_children(self, instance):
        if "children" not in self.fields:
            return
        elif isinstance(instance, dict):
            return []
        else:
            queryset = instance.children.all()
            return CategorySerializer(
                queryset,
                many=True,
                fields=self.fields,
            ).data

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.status = validated_data.get("status", instance.status)
        return instance

    def save(self):
        uuid = self.validated_data.pop("uuid", None)
        if uuid is None:
            return Category.objects.create(**self.validated_data)
        return Category.objects.update_or_create(
            uuid=uuid,
            defaults=self.validated_data,
            create_defaults=self.validated_data,
        )[0]


class PictureCustomRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        queryset = UploadFile.objects.filter(id=value)
        return queryset.first().uuid

    def to_internal_value(self, value):
        instance = UploadFile.objects.filter(uuid=value).first()
        if instance is None:
            raise serializers.ValidationError(
                detail="Picture does not exists",
                code="invalid picture",
            )
        return instance.id


class ProductSerializer(BaseSerializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=100)
    stocks = serializers.IntegerField(min_value=1)
    price = serializers.FloatField(min_value=0.1)

    cid = CategoryCustomRelatedField(
        source="category_id",
        queryset=Category.objects.all(),
        allow_null=True,
    )
    pic = PictureCustomRelatedField(
        source="picture_id",
        queryset=UploadFile.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = "__all__"

    def save(self):
        uuid = self.validated_data.pop("uuid", None)
        if uuid is None:
            return Product.objects.create(**self.validated_data)
        return Product.objects.update_or_create(
            uuid=uuid,
            defaults=self.validated_data,
            create_defaults=self.validated_data,
        )[0]
