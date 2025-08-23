from typing import List

from django.db.models import TextField
from django.db.models.functions import Cast


from apps.core.models import UserRole

# Write your functions here


def fetch_user_roles(request) -> List[UserRole]:
    roles: List[UserRole]
    if request.session["is_master"]:
        roles = list(
            UserRole.objects.all()
            .annotate(str_uuid=Cast("uuid", output_field=TextField()))
            .only("uuid")
            .values_list(
                "str_uuid",
                flat=True,
            )
        )
    else:
        roles = list(
            UserRole.objects.filter(user=request.user)
            .annotate(str_uuid=Cast("uuid", output_field=TextField()))
            .only("uuid")
            .values_list("str_uuid", flat=True)
        )
    return roles
