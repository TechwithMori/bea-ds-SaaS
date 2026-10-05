from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet, InquiryViewSet, RetentionTriggerViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="customer")
router.register("inquiries", InquiryViewSet, basename="inquiry")
router.register("retention-triggers", RetentionTriggerViewSet, basename="retention-trigger")

urlpatterns = router.urls
