from django.urls import path

from apps.core.api.v1.views import DropdownAV, UserLoginAV, UserRegisterAV

# Write your urls here

urlpatterns = [
    path(
        "dropdown/",
        DropdownAV.as_view(),
    ),
    path(
        "user/login/",
        UserLoginAV.as_view(),
    ),
    path(
        "user/register/",
        UserRegisterAV.as_view(),
    ),
]
