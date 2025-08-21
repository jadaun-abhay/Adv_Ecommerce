from django.urls import path

from apps.warehouse.api.v1.views import CategoryAV, ProductAV

# Write your urls here

urlpatterns = [
    path(
        "categories/",
        CategoryAV.as_view(),
    ),
    path(
        "products/",
        ProductAV.as_view(),
    ),
]
