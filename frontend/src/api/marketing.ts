import type { ChannelIntegration, ContentAsset, MarketingHook } from "./types";
import { api, getList } from "./client";

export function fetchAssets() {
  return getList<ContentAsset>("/api/v1/marketing/assets/");
}

export function fetchHooks() {
  return getList<MarketingHook>("/api/v1/marketing/hooks/");
}

export function fetchIntegrations() {
  return getList<ChannelIntegration>("/api/v1/marketing/integrations/");
}

export async function createHook(payload: Pick<MarketingHook, "headline" | "angle" | "platform">) {
  const { data } = await api.post<MarketingHook>("/api/v1/marketing/hooks/", {
    ...payload,
    status: "draft",
  });
  return data;
}

export async function updateIntegration(id: string, payload: Partial<ChannelIntegration>) {
  const { data } = await api.patch<ChannelIntegration>(`/api/v1/marketing/integrations/${id}/`, payload);
  return data;
}
