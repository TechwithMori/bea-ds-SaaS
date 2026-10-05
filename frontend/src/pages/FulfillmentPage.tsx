import { useEffect, useState } from "react";
import { fetchOrders, fetchOrderSummary, fetchRoutes } from "../api/orders";
import type { OrderRecord, OrderSummary, ShippingRoute } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Badge, PageHeader, Panel, SampleNote, toneFor } from "../components/ui";
import { sampleOrders, sampleRoutes, sampleSummary } from "../data/samples";
import { useI18n } from "../i18n/LanguageContext";
import type { MessageKey } from "../i18n/messages";
import { formatNumber, laneFor, money } from "../lib/format";

const LANES: { key: "pending" | "processing" | "shipped"; label: MessageKey }[] = [
  { key: "pending", label: "pending" },
  { key: "processing", label: "processing" },
  { key: "shipped", label: "shipped" },
];

export default function FulfillmentPage() {
  const { preview, tenant } = useAuth();
  const { lang, t, word } = useI18n();
  const [orders, setOrders] = useState<OrderRecord[]>(sampleOrders);
  const [summary, setSummary] = useState<OrderSummary>(sampleSummary);
  const [routes, setRoutes] = useState<ShippingRoute[]>(sampleRoutes);
  const [orderSample, setOrderSample] = useState(true);
  const [routeSample, setRouteSample] = useState(true);

  useEffect(() => {
    if (preview) {
      setOrders(sampleOrders);
      setSummary(sampleSummary);
      setRoutes(sampleRoutes);
      setOrderSample(true);
      setRouteSample(true);
      return;
    }
    let cancelled = false;
    void Promise.all([fetchOrders(), fetchOrderSummary(), fetchRoutes()])
      .then(([liveOrders, liveSummary, liveRoutes]) => {
        if (cancelled) return;
        setOrders(liveOrders.length ? liveOrders : sampleOrders);
        setSummary(liveOrders.length ? liveSummary : sampleSummary);
        setRoutes(liveRoutes.length ? liveRoutes : sampleRoutes);
        setOrderSample(liveOrders.length === 0);
        setRouteSample(liveRoutes.length === 0);
      })
      .catch(() => {
        if (!cancelled) {
          setOrderSample(true);
          setRouteSample(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [preview]);

  return (
    <div>
      <PageHeader
        desk={t("logisticsDesk")}
        title={t("fulfillment")}
        lede={t("fulfillmentLede")}
      />
      <SampleNote show={orderSample}>{t("sampleOrders")}</SampleNote>
      <div className="grid gap-4 lg:grid-cols-3">
        {LANES.map((lane) => (
          <section key={lane.key}>
            <div className="mb-3 flex items-baseline justify-between">
              <h2 className="font-display text-2xl">{t(lane.label)}</h2>
              <span className="text-sm text-ink-soft">{formatNumber(summary[lane.key], lang)}</span>
            </div>
            <div className="space-y-3">
              {orders.filter((order) => laneFor(order.status) === lane.key).map((order) => (
                <Panel key={order.id}>
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm">{order.number}</p>
                    <Badge tone={toneFor(order.status)}>{word(order.status)}</Badge>
                  </div>
                  <p className="mt-2">{order.customer_name}</p>
                  <p className="text-sm text-ink-soft">{order.shipping_address.country} · {order.route_name || t("unrouted")} · {order.route_carrier}</p>
                  <p className="mt-2 text-sm">{money(order.total, order.currency || tenant?.currency, lang)}</p>
                  {order.tracking_number ? <p className="mt-1 text-xs text-ink-soft">{order.tracking_carrier} {order.tracking_number}</p> : null}
                </Panel>
              ))}
            </div>
          </section>
        ))}
      </div>
      <h2 className="mb-3 mt-8 font-display text-2xl">{t("shippingLanes")}</h2>
      <SampleNote show={routeSample && !orderSample}>{t("sampleRoutes")}</SampleNote>
      <div className="grid gap-3 md:grid-cols-3">
        {routes.map((route) => (
          <Panel key={route.id}>
            <p>{route.name}</p>
            <p className="mt-1 text-sm text-ink-soft">{route.carrier} · {word(route.service_level)}</p>
            <p className="mt-3 text-xs uppercase tracking-[0.14em] text-ink-soft">{route.regions.join(" · ")}</p>
          </Panel>
        ))}
      </div>
    </div>
  );
}
