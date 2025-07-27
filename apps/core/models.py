import uuid6

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.enums import Status, FileType
from apps.core.managers import DeleteFilterManager

# Create your models here.


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid6.uuid6)
    status = models.IntegerField(default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DeleteFilterManager()

    class Meta:
        abstract = True


class Dropdown(BaseModel):
    label = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="children",
    )


class User(AbstractUser, BaseModel):
    email = models.EmailField(max_length=120)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class UploadFile(BaseModel):
    type: str

    def get_path(self, filename):
        pass

    file = models.FileField(upload_to=get_path)
    type = models.IntegerField(default=FileType.WAREHOUSE_IMAGES)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="files",
    )
