import type { ListingRow, SourcingOverview } from "./types";
import { api } from "./client";

export async function fetchSourcing() {
  const { data } = await api.get<SourcingOverview>("/api/v1/sourcing/overview/");
  return data;
}

export async function updateListing(id: string, payload: Partial<Pick<ListingRow, "is_published" | "retail_price">>) {
  const { data } = await api.patch(`/api/v1/store-products/${id}/`, payload);
  return data;
}
