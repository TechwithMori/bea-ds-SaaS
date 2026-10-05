import type { Bundle, StorefrontConfig } from "./types";
import { api, getList } from "./client";

export async function fetchStorefront() {
  const { data } = await api.get<StorefrontConfig>("/api/v1/storefront/config/");
  return data;
}

export async function updateStorefront(payload: Partial<StorefrontConfig>) {
  const { data } = await api.patch<StorefrontConfig>("/api/v1/storefront/config/", payload);
  return data;
}

export function fetchBundles() {
  return getList<Bundle>("/api/v1/storefront/bundles/");
}

export async function updateBundle(id: string, payload: Partial<Pick<Bundle, "is_active" | "discount_percent">>) {
  const { data } = await api.patch<Bundle>(`/api/v1/storefront/bundles/${id}/`, payload);
  return data;
}
