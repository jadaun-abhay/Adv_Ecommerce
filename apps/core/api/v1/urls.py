from django.urls import path

from apps.core.api.v1.views import DropdownAV

# Write your urls here

urlpatterns = [
    path(
        "dropdown/",
        DropdownAV.as_view(),
    ),
]
