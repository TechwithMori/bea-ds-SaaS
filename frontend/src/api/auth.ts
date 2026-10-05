import type { Tenant, User } from "./types";
import { api } from "./client";

export async function register(payload: {
  email: string;
  password: string;
  company_name?: string;
  first_name?: string;
}) {
  const { data } = await api.post<User>("/api/v1/auth/register/", payload);
  return data;
}

export async function obtainToken(email: string, password: string) {
  const { data } = await api.post<{ access: string; refresh: string }>("/api/v1/auth/token/", {
    email,
    password,
  });
  return data;
}

export async function fetchMe() {
  const { data } = await api.get<User>("/api/v1/auth/me/");
  return data;
}

export async function fetchTenants() {
  const { data } = await api.get<Tenant[] | { results: Tenant[] }>("/api/v1/tenants/");
  return Array.isArray(data) ? data : data.results;
}

export async function createTenant(name: string) {
  const { data } = await api.post<Tenant>("/api/v1/tenants/", { name });
  return data;
}
