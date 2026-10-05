import { useState, type FormEvent } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { errorMessage } from "../api/client";
import { LanguageSwitch, useI18n } from "../i18n/LanguageContext";
import type { MessageKey } from "../i18n/messages";

const NAV: { to: string; label: MessageKey; desk: MessageKey }[] = [
  { to: "/catalog", label: "catalog", desk: "sourcing" },
  { to: "/marketing", label: "marketing", desk: "growth" },
  { to: "/storefront", label: "storefront", desk: "cro" },
  { to: "/fulfillment", label: "fulfillment", desk: "logistics" },
  { to: "/customers", label: "customers", desk: "retention" },
  { to: "/finance", label: "finance", desk: "analytics" },
];

export default function AppShell() {
  const { preview, user, tenant, tenants, logout, selectTenant, openStore } = useAuth();
  const { t, word } = useI18n();
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen md:grid md:grid-cols-[16.5rem_1fr]">
      <aside className={`${open ? "block" : "hidden"} border-b border-white/10 bg-espresso text-cream md:block md:min-h-screen md:border-b-0`}>
        <div className="flex items-center justify-between px-5 py-6">
          <div>
            <p className="font-display text-3xl italic leading-none">Bea</p>
            <p className="mt-1 text-[11px] uppercase tracking-[0.28em] text-blush">{t("brandDrops")}</p>
          </div>
          <button className="text-sm text-cream/70 md:hidden" onClick={() => setOpen(false)} type="button">
            {t("close")}
          </button>
        </div>
        <nav className="px-3 pb-8">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `mb-1 flex items-baseline justify-between rounded-2xl px-3 py-3 text-sm ${
                  isActive ? "bg-white/10 text-cream" : "text-cream/70 hover:bg-white/5 hover:text-cream"
                }`
              }
            >
              <span>{t(item.label)}</span>
              <span className="text-[10px] uppercase tracking-[0.16em] text-blush">{t(item.desk)}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="min-w-0">
        <header className="flex flex-wrap items-center gap-3 border-b border-line px-4 py-4 md:px-8">
          <button className="rounded-full border border-line px-3 py-1.5 text-sm md:hidden" onClick={() => setOpen(true)} type="button">
            {t("desks")}
          </button>
          <div className="min-w-0 flex-1">
            <p className="truncate font-display text-xl">{preview ? "Lumen Atelier" : tenant?.name}</p>
            <p className="text-xs uppercase tracking-[0.16em] text-ink-soft">
              {preview ? t("sampleTour") : `${word(tenant?.plan ?? "")} · ${word(tenant?.status ?? "")}`}
            </p>
          </div>
          {!preview && tenants.length > 1 ? (
            <select
              className="rounded-full border border-line bg-cream px-3 py-2 text-sm"
              value={tenant?.slug ?? ""}
              onChange={(event) => selectTenant(event.target.value)}
            >
              {tenants.map((store) => (
                <option key={store.id} value={store.slug}>
                  {store.name}
                </option>
              ))}
            </select>
          ) : null}
          <span className="hidden text-sm text-ink-soft sm:inline">{preview ? "tour@bea.drops" : user?.email}</span>
          <LanguageSwitch />
          <button className="rounded-full bg-ink px-4 py-2 text-sm text-cream" onClick={logout} type="button">
            {t("signOut")}
          </button>
        </header>
        <main className="px-4 py-8 md:px-8">
          {preview || tenant ? <Outlet key={preview ? "preview" : tenant?.slug} /> : <OpenStore onCreate={openStore} />}
        </main>
      </div>
    </div>
  );
}

function OpenStore({ onCreate }: { onCreate: (name: string) => Promise<void> }) {
  const { t } = useI18n();
  const [name, setName] = useState("Glow Lab");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      await onCreate(name);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit} className="mx-auto max-w-lg rounded-3xl border border-line bg-cream p-8 shadow-card">
      <p className="text-[11px] uppercase tracking-[0.22em] text-blush">{t("newStore")}</p>
      <h1 className="mt-2 font-display text-4xl">{t("nameTheShop")}</h1>
      <p className="mt-3 text-sm leading-6 text-ink-soft">{t("nameTheShopBody")}</p>
      <label className="mt-6 block text-sm">
        {t("storeName")}
        <input
          className="mt-2 w-full rounded-2xl border border-line bg-paper px-4 py-3"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
      </label>
      {error ? <p className="mt-3 text-sm text-[#8d3d32]">{error}</p> : null}
      <button className="mt-6 rounded-full bg-ink px-5 py-3 text-sm text-cream" disabled={pending} type="submit">
        {pending ? t("opening") : t("openDesks")}
      </button>
    </form>
  );
}
