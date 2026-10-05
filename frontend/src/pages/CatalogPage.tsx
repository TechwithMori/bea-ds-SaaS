import { useEffect, useState } from "react";
import { fetchSourcing, updateListing } from "../api/catalog";
import type { ListingRow, SourcingOverview } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Badge, PageHeader, Panel, SampleNote, toneFor } from "../components/ui";
import { sampleSourcing } from "../data/samples";
import { money, titleCase } from "../lib/format";

export default function CatalogPage() {
  const { preview, tenant } = useAuth();
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
        desk="Sourcing desk"
        title="Catalog"
        lede="Vetted cosmetics, the gap between wholesale and retail, ingredient compliance, and whether the supplier feed is current."
      />
      <SampleNote show={catalogSample}>
        {catalogSample ? "Illustrative catalog. Supplier products replace this once they are loaded." : null}
      </SampleNote>
      <div className="mb-4 flex flex-wrap gap-2">
        {data.suppliers.map((supplier) => (
          <span key={supplier.id} className="inline-flex items-center gap-2 rounded-full border border-line bg-cream px-3 py-1.5 text-sm">
            {supplier.name}
            <Badge tone={toneFor(supplier.sync_status)}>{supplier.sync_status === "ok" ? "Synced" : titleCase(supplier.sync_status)}</Badge>
          </span>
        ))}
      </div>
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <Panel><p className="text-sm text-ink-soft">Compliant</p><p className="font-display text-3xl">{data.compliance.compliant}</p></Panel>
        <Panel><p className="text-sm text-ink-soft">In review</p><p className="font-display text-3xl">{data.compliance.pending_review}</p></Panel>
        <Panel><p className="text-sm text-ink-soft">Restricted</p><p className="font-display text-3xl">{data.compliance.restricted}</p></Panel>
      </div>
      <Panel className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="text-[11px] uppercase tracking-[0.16em] text-ink-soft">
            <tr>
              <th className="pb-3 font-normal">Product</th>
              <th className="pb-3 font-normal">Wholesale</th>
              <th className="pb-3 font-normal">Retail</th>
              <th className="pb-3 font-normal">Margin</th>
              <th className="pb-3 font-normal">Stock</th>
              <th className="pb-3 font-normal">Compliance</th>
            </tr>
          </thead>
          <tbody>
            {data.catalog.map((product) => (
              <tr key={product.id} className="border-t border-line">
                <td className="py-3 pr-4">
                  <p>{product.title}</p>
                  <p className="text-xs text-ink-soft">{titleCase(product.category)} · {product.ingredients.join(", ") || "No ingredient list"}</p>
                  {product.compliance_notes ? <p className="text-xs text-[#8a6232]">{product.compliance_notes}</p> : null}
                </td>
                <td>{money(product.wholesale_price, tenant?.currency)}</td>
                <td>{money(product.suggested_retail_price, tenant?.currency)}</td>
                <td>{product.margin_percent}%</td>
                <td>{product.stock_level}</td>
                <td><Badge tone={toneFor(product.compliance_status)}>{titleCase(product.compliance_status)}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
      <h2 className="mb-3 mt-8 font-display text-2xl">Your listings</h2>
      <SampleNote show={listingSample && !catalogSample}>These listings are an example until you publish variants into the store.</SampleNote>
      <div className="grid gap-3">
        {data.listings.map((listing) => (
          <Panel key={listing.id} className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p>{listing.title} <span className="text-ink-soft">/ {listing.variant_name}</span></p>
              <p className="text-sm text-ink-soft">
                {money(listing.wholesale_price, tenant?.currency)} wholesale · {money(listing.retail_price, tenant?.currency)} retail · {listing.margin_percent}% margin
              </p>
            </div>
            <button
              type="button"
              onClick={() => void togglePublished(listing)}
              className={`rounded-full px-4 py-2 text-sm ${listing.is_published ? "bg-moss text-cream" : "border border-line"}`}
            >
              {listing.is_published ? "Published" : "Unpublished"}
            </button>
          </Panel>
        ))}
      </div>
    </div>
  );
}
