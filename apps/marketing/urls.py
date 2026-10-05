from rest_framework.routers import DefaultRouter

from .views import AdSpendViewSet, ChannelIntegrationViewSet, ContentAssetViewSet, MarketingHookViewSet

router = DefaultRouter()
router.register("marketing/assets", ContentAssetViewSet, basename="marketing-asset")
router.register("marketing/hooks", MarketingHookViewSet, basename="marketing-hook")
router.register("marketing/integrations", ChannelIntegrationViewSet, basename="marketing-integration")
router.register("marketing/spend", AdSpendViewSet, basename="marketing-spend")

urlpatterns = router.urls
