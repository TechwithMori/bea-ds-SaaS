from rest_framework.routers import DefaultRouter

from .views import CatalogViewSet, StoreProductViewSet

router = DefaultRouter()
router.register("catalog", CatalogViewSet, basename="catalog")
router.register("store-products", StoreProductViewSet, basename="store-product")

urlpatterns = router.urls
