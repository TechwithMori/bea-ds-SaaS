import { useEffect, useState } from "react";
import { fetchBundles, fetchStorefront, updateBundle, updateStorefront } from "../api/storefront";
import type { Bundle, StorefrontConfig } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { PageHeader, Panel, SampleNote } from "../components/ui";
import { sampleBundles, sampleStorefront } from "../data/samples";
import { useI18n } from "../i18n/LanguageContext";
import type { MessageKey } from "../i18n/messages";
import { formatNumber, money, percent } from "../lib/format";

const THEMES: Record<string, { label: string; note: MessageKey; primary: string; accent: string }> = {
  atelier: { label: "Atelier", note: "themeAtelier", primary: "#241910", accent: "#C9847A" },
  clinique: { label: "Clinique", note: "themeClinique", primary: "#1d3c34", accent: "#d7c4a3" },
  noir: { label: "Noir", note: "themeNoir", primary: "#141414", accent: "#c6a15b" },
  sol: { label: "Sol", note: "themeSol", primary: "#8c3d2f", accent: "#f0d7b4" },
};

export default function StorefrontPage() {
  const { preview, tenant } = useAuth();
  const { lang, t } = useI18n();
  const [config, setConfig] = useState<StorefrontConfig>(sampleStorefront);
  const [bundles, setBundles] = useState<Bundle[]>(sampleBundles);
  const [bundleSample, setBundleSample] = useState(true);
  const [offline, setOffline] = useState(preview);
  const [saved, setSaved] = useState("");

  useEffect(() => {
    if (preview) {
      setConfig(sampleStorefront);
      setBundles(sampleBundles);
      setBundleSample(true);
      setOffline(true);
      return;
    }
    let cancelled = false;
    void Promise.all([fetchStorefront(), fetchBundles()])
      .then(([liveConfig, liveBundles]) => {
        if (cancelled) return;
        setConfig(liveConfig);
        setBundles(liveBundles.length ? liveBundles : sampleBundles);
        setBundleSample(liveBundles.length === 0);
        setOffline(false);
      })
      .catch(() => {
        if (!cancelled) {
          setBundleSample(true);
          setOffline(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [preview]);

  function patchLocal(partial: Partial<StorefrontConfig>) {
    setConfig((current) => ({ ...current, ...partial }));
    setSaved("");
  }

  async function save() {
    if (preview || offline) {
      setSaved(t("previewOnly"));
      return;
    }
    setSaved(t("saving"));
    try {
      const next = await updateStorefront({
        theme: config.theme,
        font_pairing: config.font_pairing,
        primary_color: config.primary_color,
        accent_color: config.accent_color,
        announcement: config.announcement,
        show_reviews: config.show_reviews,
        show_urgency: config.show_urgency,
        show_bundles: config.show_bundles,
        free_shipping_threshold: config.free_shipping_threshold,
      });
      setConfig(next);
      setSaved(t("shopSaved"));
    } catch {
      setSaved(t("shopSaveFailed"));
    }
  }

  async function toggleBundle(bundle: Bundle) {
    const is_active = !bundle.is_active;
    setBundles((current) => current.map((row) => (row.id === bundle.id ? { ...row, is_active } : row)));
    if (bundleSample || preview) return;
    try {
      await updateBundle(bundle.id, { is_active });
    } catch {
      setBundles((current) => current.map((row) => (row.id === bundle.id ? bundle : row)));
    }
  }

  return (
    <div>
      <PageHeader
        desk={t("shopDesk")}
        title={t("storefront")}
        lede={t("storefrontLede")}
      />
      <SampleNote show={bundleSample}>{t("sampleBundles")}</SampleNote>
      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          <Panel>
            <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">{t("theme")}</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {Object.entries(THEMES).map(([key, theme]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => patchLocal({ theme: key, primary_color: theme.primary, accent_color: theme.accent })}
                  className={`rounded-2xl border p-4 text-start ${config.theme === key ? "border-ink" : "border-line"}`}
                >
                  <span className="mb-3 flex gap-2">
                    <i className="h-8 w-8 rounded-full" style={{ background: theme.primary }} />
                    <i className="h-8 w-8 rounded-full" style={{ background: theme.accent }} />
                  </span>
                  <p>{theme.label}</p>
                  <p className="text-sm text-ink-soft">{t(theme.note)}</p>
                </button>
              ))}
            </div>
          </Panel>
          <Panel className="space-y-3">
            <Toggle label={t("reviewsFold")} checked={config.show_reviews} onChange={(show_reviews) => patchLocal({ show_reviews })} />
            <Toggle label={t("lowStock")} checked={config.show_urgency} onChange={(show_urgency) => patchLocal({ show_urgency })} />
            <Toggle label={t("bundleModule")} checked={config.show_bundles} onChange={(show_bundles) => patchLocal({ show_bundles })} />
            <label className="block text-sm">
              {t("announcement")}
              <input className="mt-2 w-full rounded-2xl border border-line bg-paper px-3 py-2" value={config.announcement} onChange={(event) => patchLocal({ announcement: event.target.value })} />
            </label>
            <label className="block text-sm">
              {t("freeShipping")}
              <input className="mt-2 w-full rounded-2xl border border-line bg-paper px-3 py-2" value={config.free_shipping_threshold} onChange={(event) => patchLocal({ free_shipping_threshold: event.target.value })} />
            </label>
            <button className="rounded-full bg-ink px-4 py-2 text-sm text-cream" type="button" onClick={() => void save()}>{t("saveShop")}</button>
            {saved ? <p className="text-sm text-ink-soft">{saved}</p> : null}
          </Panel>
        </div>
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">{t("preview")}</p>
          <div className="mt-4 overflow-hidden rounded-3xl" style={{ background: config.primary_color, color: "#faf7f2" }}>
            <p className="px-5 py-2 text-center text-xs" style={{ background: config.accent_color, color: config.primary_color }}>{config.announcement || t("announcementBar")}</p>
            <div className="p-6">
              <p className="font-display text-3xl">Calm Repair Serum</p>
              <p className="mt-2 text-sm opacity-80">{t("previewBlurb")}</p>
              <p className="mt-6 font-display text-2xl">{money("78", tenant?.currency || "USD", lang)}</p>
              {config.show_reviews ? <p className="mt-3 text-xs opacity-80">{t("calmByThursday", { count: formatNumber(128, lang) })}</p> : null}
              {config.show_urgency ? <p className="mt-2 text-xs">{t("leftAtLab", { count: formatNumber(40, lang) })}</p> : null}
              <div className="mt-6 rounded-full px-4 py-2 text-center text-sm" style={{ background: config.accent_color, color: config.primary_color }}>{t("addToRitual")}</div>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {bundles.map((bundle) => (
              <div key={bundle.id} className="rounded-2xl border border-line p-4">
                <div className="flex items-center justify-between gap-3">
                  <p>{bundle.name}</p>
                  <button type="button" className="text-sm underline" onClick={() => void toggleBundle(bundle)}>
                    {bundle.is_active ? t("active") : t("paused")}
                  </button>
                </div>
                <p className="mt-1 text-sm text-ink-soft">{bundle.description}</p>
                <p className="mt-2 text-sm">{t("percentOff", { count: percent(bundle.discount_percent, lang) })} · {bundle.items.map((item) => item.title).join(" + ")}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-4 text-sm">
      {label}
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}
