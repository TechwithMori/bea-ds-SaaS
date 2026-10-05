import { useEffect, useState } from "react";
import { fetchSourcing, updateListing } from "../api/catalog";
import type { ListingRow, SourcingOverview } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Badge, PageHeader, Panel, SampleNote, toneFor } from "../components/ui";
import { sampleSourcing } from "../data/samples";
import { useI18n } from "../i18n/LanguageContext";
import { formatNumber, money, percent } from "../lib/format";

export default function CatalogPage() {
  const { preview, tenant } = useAuth();
  const { lang, t, word } = useI18n();
  const [data, setData] = useState<SourcingOverview>(sampleSourcing);
  const [catalogSample, setCatalogSample] = useState(true);
  const [listingSample, setListingSample] = useState(true);

  useEffect(() => {
    if (preview) {
      setData(sampleSourcing);
      setCatalogSample(true);
      setListingSample(true);
      return;
    }
    let cancelled = false;
    void fetchSourcing()
      .then((live) => {
        if (cancelled) return;
        setData({
          suppliers: live.suppliers.length ? live.suppliers : sampleSourcing.suppliers,
          compliance: live.catalog.length ? live.compliance : sampleSourcing.compliance,
          catalog: live.catalog.length ? live.catalog : sampleSourcing.catalog,
          listings: live.listings.length ? live.listings : sampleSourcing.listings,
        });
        setCatalogSample(live.catalog.length === 0);
        setListingSample(live.listings.length === 0);
      })
      .catch(() => {
        if (!cancelled) {
          setData(sampleSourcing);
          setCatalogSample(true);
          setListingSample(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [preview]);

  async function togglePublished(listing: ListingRow) {
    const next = !listing.is_published;
    setData((current) => ({
      ...current,
      listings: current.listings.map((row) => (row.id === listing.id ? { ...row, is_published: next } : row)),
    }));
    if (listingSample || preview) return;
    try {
      await updateListing(listing.id, { is_published: next });
    } catch {
      setData((current) => ({
        ...current,
        listings: current.listings.map((row) => (row.id === listing.id ? { ...row, is_published: listing.is_published } : row)),
      }));
    }
  }

  return (
    <div>
      <PageHeader
        desk={t("sourcingDesk")}
        title={t("catalog")}
        lede={t("catalogLede")}
      />
      <SampleNote show={catalogSample}>
        {catalogSample ? t("sampleCatalog") : null}
      </SampleNote>
      <div className="mb-4 flex flex-wrap gap-2">
        {data.suppliers.map((supplier) => (
          <span key={supplier.id} className="inline-flex items-center gap-2 rounded-full border border-line bg-cream px-3 py-1.5 text-sm">
            {supplier.name}
            <Badge tone={toneFor(supplier.sync_status)}>{word(supplier.sync_status)}</Badge>
          </span>
        ))}
      </div>
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <Panel><p className="text-sm text-ink-soft">{t("compliant")}</p><p className="font-display text-3xl">{formatNumber(data.compliance.compliant, lang)}</p></Panel>
        <Panel><p className="text-sm text-ink-soft">{t("inReview")}</p><p className="font-display text-3xl">{formatNumber(data.compliance.pending_review, lang)}</p></Panel>
        <Panel><p className="text-sm text-ink-soft">{t("restricted")}</p><p className="font-display text-3xl">{formatNumber(data.compliance.restricted, lang)}</p></Panel>
      </div>
      <Panel className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-start text-sm">
          <thead className="text-[11px] uppercase tracking-[0.16em] text-ink-soft">
            <tr>
              <th className="pb-3 font-normal">{t("product")}</th>
              <th className="pb-3 font-normal">{t("wholesale")}</th>
              <th className="pb-3 font-normal">{t("retail")}</th>
              <th className="pb-3 font-normal">{t("margin")}</th>
              <th className="pb-3 font-normal">{t("stock")}</th>
              <th className="pb-3 font-normal">{t("compliance")}</th>
            </tr>
          </thead>
          <tbody>
            {data.catalog.map((product) => (
              <tr key={product.id} className="border-t border-line">
                <td className="py-3 pe-4">
                  <p>{product.title}</p>
                  <p className="text-xs text-ink-soft">{word(product.category)} · {product.ingredients.join(", ") || t("noIngredients")}</p>
                  {product.compliance_notes ? <p className="text-xs text-[#8a6232]">{product.compliance_notes}</p> : null}
                </td>
                <td>{money(product.wholesale_price, tenant?.currency, lang)}</td>
                <td>{money(product.suggested_retail_price, tenant?.currency, lang)}</td>
                <td>{percent(product.margin_percent, lang)}</td>
                <td>{formatNumber(product.stock_level, lang)}</td>
                <td><Badge tone={toneFor(product.compliance_status)}>{word(product.compliance_status)}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
      <h2 className="mb-3 mt-8 font-display text-2xl">{t("yourListings")}</h2>
      <SampleNote show={listingSample && !catalogSample}>{t("sampleListings")}</SampleNote>
      <div className="grid gap-3">
        {data.listings.map((listing) => (
          <Panel key={listing.id} className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p>{listing.title} <span className="text-ink-soft">/ {listing.variant_name}</span></p>
              <p className="text-sm text-ink-soft">
                {t("wholesaleRetail", {
                  wholesale: money(listing.wholesale_price, tenant?.currency, lang),
                  retail: money(listing.retail_price, tenant?.currency, lang),
                  margin: percent(listing.margin_percent, lang),
                })}
              </p>
            </div>
            <button
              type="button"
              onClick={() => void togglePublished(listing)}
              className={`rounded-full px-4 py-2 text-sm ${listing.is_published ? "bg-moss text-cream" : "border border-line"}`}
            >
              {listing.is_published ? t("published") : t("unpublished")}
            </button>
          </Panel>
        ))}
      </div>
    </div>
  );
}
