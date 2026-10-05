import type { CustomerRecord, Inquiry, RetentionTrigger } from "./types";
import { api, getList } from "./client";

export function fetchCustomers() {
  return getList<CustomerRecord>("/api/v1/customers/");
}

export function fetchInquiries() {
  return getList<Inquiry>("/api/v1/inquiries/");
}

export function fetchTriggers() {
  return getList<RetentionTrigger>("/api/v1/retention-triggers/");
}

export async function createInquiry(payload: Pick<Inquiry, "customer_name" | "customer_email" | "subject" | "body" | "channel">) {
  const { data } = await api.post<Inquiry>("/api/v1/inquiries/", payload);
  return data;
}

export async function updateInquiry(id: string, status: string) {
  const { data } = await api.patch<Inquiry>(`/api/v1/inquiries/${id}/`, { status });
  return data;
}

export async function updateTrigger(id: string, is_enabled: boolean) {
  const { data } = await api.patch<RetentionTrigger>(`/api/v1/retention-triggers/${id}/`, { is_enabled });
  return data;
}
