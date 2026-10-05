from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CatalogViewSet, SourcingOverviewView, StoreProductViewSet

router = DefaultRouter()
router.register("catalog", CatalogViewSet, basename="catalog")
router.register("store-products", StoreProductViewSet, basename="store-product")

urlpatterns = [
    path("sourcing/overview/", SourcingOverviewView.as_view(), name="sourcing-overview"),
    *router.urls,
]
