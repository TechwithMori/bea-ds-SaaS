from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BundleViewSet, StorefrontSettingsView

router = DefaultRouter()
router.register("storefront/bundles", BundleViewSet, basename="storefront-bundle")

urlpatterns = [
    path("storefront/config/", StorefrontSettingsView.as_view(), name="storefront-config"),
    *router.urls,
]
