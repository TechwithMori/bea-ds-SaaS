from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, ShippingRouteViewSet, SupplierFulfillmentWebhookView

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")
router.register("shipping-routes", ShippingRouteViewSet, basename="shipping-route")

urlpatterns = [
    path(
        "webhooks/supplier-fulfillment/",
        SupplierFulfillmentWebhookView.as_view(),
        name="supplier-fulfillment-webhook",
    ),
    *router.urls,
]
