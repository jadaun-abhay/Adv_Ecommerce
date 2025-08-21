from django.db import models

from apps.core.models import BaseModel, UploadFile

# Create your models here.


class Category(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="children",
    )


class Product(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    stocks = models.IntegerField(default=1)
    price = models.FloatField(default=0.1)
    picture = models.OneToOneField(
        UploadFile,
        on_delete=models.SET_NULL,
        null=True,
        parent_link=False,
        related_name="image",
    )
