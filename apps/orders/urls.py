from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, SupplierFulfillmentWebhookView

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path(
        "webhooks/supplier-fulfillment/",
        SupplierFulfillmentWebhookView.as_view(),
        name="supplier-fulfillment-webhook",
    ),
    *router.urls,
]
