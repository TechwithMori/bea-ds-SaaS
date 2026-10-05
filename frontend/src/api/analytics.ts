import type { AnalyticsOverview } from "./types";
import { api } from "./client";

export async function fetchAnalytics(days: 7 | 30 | 90) {
  const { data } = await api.get<AnalyticsOverview>("/api/v1/analytics/overview/", { params: { days } });
  return data;
}
