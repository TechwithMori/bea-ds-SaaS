import { useEffect, useState } from "react";
import { fetchAnalytics } from "../api/analytics";
import type { AnalyticsOverview } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { PageHeader, Panel, SampleNote, Stat } from "../components/ui";
import { sampleAnalytics } from "../data/samples";
import { money, titleCase } from "../lib/format";

export default function FinancePage() {
  const { preview, tenant } = useAuth();
  const [days, setDays] = useState<7 | 30 | 90>(30);
  const [data, setData] = useState<AnalyticsOverview>(sampleAnalytics);
  const [illustrative, setIllustrative] = useState(true);

  useEffect(() => {
    if (preview) {
      setData({ ...sampleAnalytics, days });
      setIllustrative(true);
      return;
    }
    let cancelled = false;
    void fetchAnalytics(days)
      .then((live) => {
        if (cancelled) return;
        if (live.order_count === 0) {
          setData({ ...sampleAnalytics, days, currency: tenant?.currency || "USD" });
          setIllustrative(true);
          return;
        }
        setData(live);
        setIllustrative(false);
      })
      .catch(() => {
        if (!cancelled) {
          setData({ ...sampleAnalytics, days });
          setIllustrative(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [days, preview, tenant?.currency]);

  const max = Math.max(...data.series.map((point) => Number(point.revenue)), 1);

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-end justify-between gap-4">
        <PageHeader
          desk="Finance desk"
          title="The books"
          lede="Revenue, what an order is worth, what a customer costs to win, and what remains after product and media."
        />
        <div className="mb-8 flex gap-2">
          {([7, 30, 90] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setDays(option)}
              className={`rounded-full px-3 py-1.5 text-sm ${days === option ? "bg-ink text-cream" : "border border-line"}`}
            >
              {option}d
            </button>
          ))}
        </div>
      </div>
      <SampleNote show={illustrative} />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Stat label="Revenue" value={money(data.revenue, data.currency)} detail={`${data.order_count} settled orders`} />
        <Stat label="Average order" value={money(data.aov, data.currency)} detail={`${data.new_customers} buyers in window`} />
        <Stat label="Acquisition cost" value={data.cac ? money(data.cac, data.currency) : "—"} detail={`${money(data.ad_spend, data.currency)} media`} />
        <Stat label="Net margin" value={`${data.net_margin_percent}%`} detail={`${money(data.net_profit, data.currency)} after cost and ads`} />
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Revenue</p>
          <div className="mt-6 flex h-48 items-end gap-2">
            {data.series.map((point) => (
              <div key={point.day} className="flex h-full flex-1 flex-col justify-end">
                <div
                  className="rounded-t-md bg-ink"
                  style={{ height: `${Math.max(8, (Number(point.revenue) / max) * 100)}%` }}
                  title={`${point.day} ${money(point.revenue, data.currency)}`}
                />
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Where it went</p>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="flex justify-between"><span>Product cost</span><span>{money(data.cogs, data.currency)}</span></li>
            <li className="flex justify-between"><span>Gross profit</span><span>{money(data.gross_profit, data.currency)}</span></li>
            {data.spend_by_channel.map((row) => (
              <li key={row.channel} className="flex justify-between text-ink-soft">
                <span>{titleCase(row.channel)}</span>
                <span>{money(row.amount, data.currency)}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
      <Panel className="mt-4">
        <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">What sold</p>
        <ul className="mt-4 divide-y divide-line">
          {data.top_products.map((product) => (
            <li key={product.title} className="flex items-center justify-between py-3 text-sm">
              <span>{product.title}</span>
              <span className="text-ink-soft">{product.units} units · {money(product.revenue, data.currency)}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
