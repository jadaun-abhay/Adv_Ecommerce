from django.db import models

from apps.core.enums import Status

# Write your managers here


class DeleteFilterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status=Status.DELETED)
