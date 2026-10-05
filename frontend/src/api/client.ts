import axios, { type AxiosResponse } from "axios";

const ACCESS = "bea.access";
const REFRESH = "bea.refresh";
const TENANT = "bea.tenant";

export const api = axios.create({ baseURL: "" });

api.interceptors.request.use((config) => {
  const access = localStorage.getItem(ACCESS);
  const slug = localStorage.getItem(TENANT);
  if (access) config.headers.Authorization = `Bearer ${access}`;
  if (slug) config.headers["X-Tenant-Slug"] = slug;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (!original || original._retried || error.response?.status !== 401) {
      return Promise.reject(error);
    }
    const refresh = localStorage.getItem(REFRESH);
    if (!refresh || original.url?.includes("/auth/token/")) {
      return Promise.reject(error);
    }
    original._retried = true;
    const { data } = await axios.post("/api/v1/auth/token/refresh/", { refresh });
    localStorage.setItem(ACCESS, data.access);
    if (data.refresh) localStorage.setItem(REFRESH, data.refresh);
    original.headers.Authorization = `Bearer ${data.access}`;
    return api(original);
  },
);

type Page<T> = { results?: T[]; next?: string | null };

export async function getList<T>(url: string): Promise<T[]> {
  const rows: T[] = [];
  let next: string | null = url;
  for (let guard = 0; next && guard < 5; guard += 1) {
    const response: AxiosResponse<Page<T> | T[]> = await api.get(next);
    const data: Page<T> | T[] = response.data;
    if (Array.isArray(data)) return data;
    rows.push(...(data.results ?? []));
    next = data.next ? toPath(data.next) : null;
  }
  return rows;
}

function toPath(url: string) {
  if (url.startsWith("http")) {
    const parsed = new URL(url);
    return parsed.pathname + parsed.search;
  }
  return url;
}

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined;
    if (!data) return "The desk could not reach the API.";
    if (typeof data.detail === "string") return data.detail;
    const first = Object.values(data)[0];
    if (Array.isArray(first) && first.length) return String(first[0]);
    if (typeof first === "string") return first;
  }
  return "Something went wrong. Try again.";
}
