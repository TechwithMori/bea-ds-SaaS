import { useState, type FormEvent } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { errorMessage } from "../api/client";
import { titleCase } from "../lib/format";

const NAV = [
  { to: "/catalog", label: "Catalog", desk: "Sourcing" },
  { to: "/marketing", label: "Marketing", desk: "Growth" },
  { to: "/storefront", label: "Storefront", desk: "CRO" },
  { to: "/fulfillment", label: "Fulfillment", desk: "Logistics" },
  { to: "/customers", label: "Customers", desk: "Retention" },
  { to: "/finance", label: "Finance", desk: "Analytics" },
];

export default function AppShell() {
  const { preview, user, tenant, tenants, logout, selectTenant, openStore } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen md:grid md:grid-cols-[16.5rem_1fr]">
      <aside className={`${open ? "block" : "hidden"} border-b border-white/10 bg-espresso text-cream md:block md:min-h-screen md:border-b-0`}>
        <div className="flex items-center justify-between px-5 py-6">
          <div>
            <p className="font-display text-3xl italic leading-none">Bea</p>
            <p className="mt-1 text-[11px] uppercase tracking-[0.28em] text-blush">Drops</p>
          </div>
          <button className="text-sm text-cream/70 md:hidden" onClick={() => setOpen(false)} type="button">
            Close
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
              <span>{item.label}</span>
              <span className="text-[10px] uppercase tracking-[0.16em] text-blush">{item.desk}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="min-w-0">
        <header className="flex flex-wrap items-center gap-3 border-b border-line px-4 py-4 md:px-8">
          <button className="rounded-full border border-line px-3 py-1.5 text-sm md:hidden" onClick={() => setOpen(true)} type="button">
            Desks
          </button>
          <div className="min-w-0 flex-1">
            <p className="truncate font-display text-xl">{preview ? "Lumen Atelier" : tenant?.name}</p>
            <p className="text-xs uppercase tracking-[0.16em] text-ink-soft">
              {preview ? "Sample tour" : `${titleCase(tenant?.plan ?? "")} · ${titleCase(tenant?.status ?? "")}`}
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
          <button className="rounded-full bg-ink px-4 py-2 text-sm text-cream" onClick={logout} type="button">
            Sign out
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
      <p className="text-[11px] uppercase tracking-[0.22em] text-blush">New store</p>
      <h1 className="mt-2 font-display text-4xl">Name the shop the desks will run.</h1>
      <p className="mt-3 text-sm leading-6 text-ink-soft">
        Sourcing, growth, the storefront, logistics, retention, and finance are stood up with this store. You can publish products as soon as the catalog has stock.
      </p>
      <label className="mt-6 block text-sm">
        Store name
        <input
          className="mt-2 w-full rounded-2xl border border-line bg-paper px-4 py-3"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />
      </label>
      {error ? <p className="mt-3 text-sm text-[#8d3d32]">{error}</p> : null}
      <button className="mt-6 rounded-full bg-ink px-5 py-3 text-sm text-cream" disabled={pending} type="submit">
        {pending ? "Opening…" : "Open the desks"}
      </button>
    </form>
  );
}
