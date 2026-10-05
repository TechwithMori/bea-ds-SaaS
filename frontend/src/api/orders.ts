import type { OrderRecord, OrderSummary, ShippingRoute } from "./types";
import { api, getList } from "./client";

export function fetchOrders() {
  return getList<OrderRecord>("/api/v1/orders/");
}

export async function fetchOrderSummary() {
  const { data } = await api.get<OrderSummary>("/api/v1/orders/summary/");
  return data;
}

export function fetchRoutes() {
  return getList<ShippingRoute>("/api/v1/shipping-routes/");
}
