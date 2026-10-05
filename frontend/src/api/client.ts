import axios, { type AxiosResponse } from "axios";
import { en, fa } from "../i18n/messages";

const ACCESS = "bea.access";
const REFRESH = "bea.refresh";
const TENANT = "bea.tenant";

export const api = axios.create({ baseURL: "" });

const API_FA: Record<string, string> = {
  "A valid store context is required.": "زمینه فروشگاه معتبر لازم است.",
  "This store cannot accept orders.": "این فروشگاه نمی‌تواند سفارش بپذیرد.",
  "This channel is already on the desk.": "این کانال از قبل روی میز است.",
  "No active account found with the given credentials": "حسابی با این مشخصات پیدا نشد.",
  "Invalid signature.": "امضا نامعتبر است.",
  "Unknown order.": "سفارش ناشناخته است.",
};

function currentLang() {
  return localStorage.getItem("bea.lang") === "en" ? "en" : "fa";
}

api.interceptors.request.use((config) => {
  const access = localStorage.getItem(ACCESS);
  const slug = localStorage.getItem(TENANT);
  if (access) config.headers.Authorization = `Bearer ${access}`;
  if (slug) config.headers["X-Tenant-Slug"] = slug;
  config.headers["Accept-Language"] = currentLang();
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
  const copy = currentLang() === "fa" ? fa : en;
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined;
    if (!data) return copy.apiUnreachable;
    if (typeof data.detail === "string") return API_FA[data.detail] && currentLang() === "fa" ? API_FA[data.detail] : data.detail;
    const first = Object.values(data)[0];
    if (Array.isArray(first) && first.length) return String(first[0]);
    if (typeof first === "string") return first;
  }
  return copy.genericError;
}
