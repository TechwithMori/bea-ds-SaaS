import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { createTenant, fetchMe, fetchTenants, obtainToken, register as registerRequest } from "../api/auth";
import type { Tenant, User } from "../api/types";

const ACCESS = "bea.access";
const REFRESH = "bea.refresh";
const TENANT = "bea.tenant";
const PREVIEW = "bea.preview";

type AuthValue = {
  ready: boolean;
  preview: boolean;
  user: User | null;
  tenant: Tenant | null;
  tenants: Tenant[];
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, companyName: string) => Promise<void>;
  logout: () => void;
  enterPreview: () => void;
  selectTenant: (slug: string) => void;
  openStore: (name: string) => Promise<void>;
};

const AuthContext = createContext<AuthValue | null>(null);

async function loadSession() {
  const me = await fetchMe();
  const stores = await fetchTenants();
  const slug = localStorage.getItem(TENANT);
  const current = stores.find((store) => store.slug === slug) ?? stores.find((store) => store.is_default) ?? stores[0] ?? null;
  if (current) localStorage.setItem(TENANT, current.slug);
  return { me, stores, current };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [preview, setPreview] = useState(sessionStorage.getItem(PREVIEW) === "1");
  const [user, setUser] = useState<User | null>(null);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [tenant, setTenant] = useState<Tenant | null>(null);

  useEffect(() => {
    const access = localStorage.getItem(ACCESS);
    if (preview || !access) {
      setReady(true);
      return;
    }
    void loadSession()
      .then(({ me, stores, current }) => {
        setUser(me);
        setTenants(stores);
        setTenant(current);
      })
      .catch(() => {
        localStorage.removeItem(ACCESS);
        localStorage.removeItem(REFRESH);
      })
      .finally(() => setReady(true));
  }, [preview]);

  async function login(email: string, password: string) {
    const tokens = await obtainToken(email, password);
    localStorage.setItem(ACCESS, tokens.access);
    localStorage.setItem(REFRESH, tokens.refresh);
    sessionStorage.removeItem(PREVIEW);
    setPreview(false);
    const { me, stores, current } = await loadSession();
    setUser(me);
    setTenants(stores);
    setTenant(current);
  }

  async function register(email: string, password: string, companyName: string) {
    await registerRequest({ email, password, company_name: companyName });
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
    localStorage.removeItem(TENANT);
    sessionStorage.removeItem(PREVIEW);
    setPreview(false);
    setUser(null);
    setTenant(null);
    setTenants([]);
  }

  function enterPreview() {
    sessionStorage.setItem(PREVIEW, "1");
    setPreview(true);
    setUser(null);
    setTenant(null);
  }

  function selectTenant(slug: string) {
    const next = tenants.find((store) => store.slug === slug) ?? null;
    if (!next) return;
    localStorage.setItem(TENANT, next.slug);
    setTenant(next);
  }

  async function openStore(name: string) {
    const created = await createTenant(name);
    localStorage.setItem(TENANT, created.slug);
    const stores = await fetchTenants();
    setTenants(stores);
    setTenant(stores.find((store) => store.slug === created.slug) ?? created);
  }

  const value: AuthValue = {
    ready,
    preview,
    user,
    tenant,
    tenants,
    login,
    register,
    logout,
    enterPreview,
    selectTenant,
    openStore,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
