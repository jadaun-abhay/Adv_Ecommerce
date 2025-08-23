import uuid6

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.enums import Status, FileType
from base.api.v1.functions import get_type_path
from apps.core.managers import DeleteFilterManager

# Create your models here.


class BaseModel(models.Model):

    BASE_MODEL_FIELDS = (
        "id",
        "status",
        "created_at",
        "updated_at",
    )

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

    def user_data(self):
        return {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "full_name": self.get_full_name(),
            "profile": self.get_profile(),
        }

    def get_profile(self):
        profile = UploadFile.objects.filter(user=self, type=FileType.PROFILE).only(
            "file"
        )
        return profile.first().file.url


class UploadFile(BaseModel):
    def get_path(self, filename):
        _path: str = get_type_path(self.type, self.user_id)
        return f"{_path}/{filename}"

    file = models.FileField(upload_to=get_path)
    type = models.IntegerField(default=FileType.WAREHOUSE_IMAGES)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="files",
    )


class Roles(BaseModel):
    role = models.CharField(max_length=15)


class UserRole(BaseModel):
    role = models.ForeignKey(
        Roles,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_roles",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="users",
    )
