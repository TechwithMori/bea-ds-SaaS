import { useEffect, useState, type FormEvent } from "react";
import { createInquiry, fetchCustomers, fetchInquiries, fetchTriggers, updateInquiry, updateTrigger } from "../api/customers";
import type { CustomerRecord, Inquiry, RetentionTrigger } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { Badge, PageHeader, Panel, SampleNote, toneFor } from "../components/ui";
import { sampleCustomers, sampleInquiries, sampleTriggers } from "../data/samples";
import { money, titleCase } from "../lib/format";

const NEXT_STATUS: Record<string, string> = { open: "waiting", waiting: "resolved", resolved: "open" };

export default function CustomersPage() {
  const { preview, tenant } = useAuth();
  const [customers, setCustomers] = useState<CustomerRecord[]>(sampleCustomers);
  const [inquiries, setInquiries] = useState<Inquiry[]>(sampleInquiries);
  const [triggers, setTriggers] = useState<RetentionTrigger[]>(sampleTriggers);
  const [buyersSample, setBuyersSample] = useState(true);
  const [inquirySample, setInquirySample] = useState(true);
  const [triggerSample, setTriggerSample] = useState(true);
  const [form, setForm] = useState({ customer_name: "", customer_email: "", subject: "", body: "", channel: "email" });

  useEffect(() => {
    if (preview) {
      setCustomers(sampleCustomers);
      setInquiries(sampleInquiries);
      setTriggers(sampleTriggers);
      setBuyersSample(true);
      setInquirySample(true);
      setTriggerSample(true);
      return;
    }
    let cancelled = false;
    void Promise.all([fetchCustomers(), fetchInquiries(), fetchTriggers()])
      .then(([liveCustomers, liveInquiries, liveTriggers]) => {
        if (cancelled) return;
        setCustomers(liveCustomers.length ? liveCustomers : sampleCustomers);
        setInquiries(liveInquiries.length ? liveInquiries : sampleInquiries);
        setTriggers(liveTriggers.length ? liveTriggers : sampleTriggers);
        setBuyersSample(liveCustomers.length === 0);
        setInquirySample(liveInquiries.length === 0);
        setTriggerSample(liveTriggers.length === 0);
      })
      .catch(() => {
        if (!cancelled) {
          setBuyersSample(true);
          setInquirySample(true);
          setTriggerSample(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [preview]);

  async function cycle(inquiry: Inquiry) {
    const status = NEXT_STATUS[inquiry.status] ?? "open";
    setInquiries((current) => current.map((row) => (row.id === inquiry.id ? { ...row, status } : row)));
    if (inquirySample || preview) return;
    try {
      await updateInquiry(inquiry.id, status);
    } catch {
      setInquiries((current) => current.map((row) => (row.id === inquiry.id ? inquiry : row)));
    }
  }

  async function toggle(trigger: RetentionTrigger) {
    const is_enabled = !trigger.is_enabled;
    setTriggers((current) => current.map((row) => (row.id === trigger.id ? { ...row, is_enabled } : row)));
    if (triggerSample || preview) return;
    try {
      await updateTrigger(trigger.id, is_enabled);
    } catch {
      setTriggers((current) => current.map((row) => (row.id === trigger.id ? trigger : row)));
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const payload = { ...form };
    setForm({ customer_name: "", customer_email: "", subject: "", body: "", channel: "email" });
    if (preview) {
      setInquiries((current) => [{ id: `local-${Date.now()}`, ...payload, status: "open" }, ...current]);
      return;
    }
    try {
      const saved = await createInquiry(payload);
      setInquirySample(false);
      setInquiries((current) => [saved, ...(inquirySample ? [] : current)]);
    } catch {
      setInquiries((current) => [{ id: `local-${Date.now()}`, ...payload, status: "open" }, ...current]);
    }
  }

  const tiers = ["member", "insider", "muse"].map((tier) => ({
    tier,
    count: customers.filter((customer) => customer.loyalty_tier === tier).length,
  }));

  return (
    <div>
      <PageHeader
        desk="Retention desk"
        title="Customers"
        lede="Questions in the inbox, the messages that leave on their own, and the people who keep coming back."
      />
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        {tiers.map((tier) => (
          <Panel key={tier.tier}>
            <p className="text-sm text-ink-soft">{titleCase(tier.tier)}</p>
            <p className="font-display text-3xl">{tier.count}</p>
          </Panel>
        ))}
      </div>
      <SampleNote show={buyersSample}>Buyer totals are illustrative until orders settle.</SampleNote>
      <Panel className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="text-[11px] uppercase tracking-[0.16em] text-ink-soft">
            <tr>
              <th className="pb-3 font-normal">Buyer</th>
              <th className="pb-3 font-normal">Tier</th>
              <th className="pb-3 font-normal">Orders</th>
              <th className="pb-3 font-normal">Lifetime</th>
              <th className="pb-3 font-normal">Points</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id} className="border-t border-line">
                <td className="py-3">
                  <p>{customer.name}</p>
                  <p className="text-xs text-ink-soft">{customer.email}</p>
                </td>
                <td><Badge tone={toneFor(customer.loyalty_tier)}>{titleCase(customer.loyalty_tier)}</Badge></td>
                <td>{customer.orders_count}</td>
                <td>{money(customer.lifetime_value, tenant?.currency)}</td>
                <td>{customer.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Inbox</p>
          <SampleNote show={inquirySample} />
          <ul className="space-y-4">
            {inquiries.map((inquiry) => (
              <li key={inquiry.id} className="border-b border-line pb-4 last:border-0">
                <div className="flex items-center justify-between gap-3">
                  <p>{inquiry.subject}</p>
                  <button type="button" onClick={() => void cycle(inquiry)}>
                    <Badge tone={toneFor(inquiry.status)}>{titleCase(inquiry.status)}</Badge>
                  </button>
                </div>
                <p className="mt-1 text-xs text-ink-soft">{inquiry.customer_name} · {titleCase(inquiry.channel)}</p>
                <p className="mt-2 text-sm leading-6">{inquiry.body}</p>
              </li>
            ))}
          </ul>
          <form onSubmit={submit} className="mt-4 space-y-2">
            <div className="grid gap-2 sm:grid-cols-2">
              <input className="rounded-2xl border border-line bg-paper px-3 py-2 text-sm" placeholder="Name" value={form.customer_name} onChange={(event) => setForm({ ...form, customer_name: event.target.value })} required />
              <input className="rounded-2xl border border-line bg-paper px-3 py-2 text-sm" type="email" placeholder="Email" value={form.customer_email} onChange={(event) => setForm({ ...form, customer_email: event.target.value })} required />
            </div>
            <input className="w-full rounded-2xl border border-line bg-paper px-3 py-2 text-sm" placeholder="Subject" value={form.subject} onChange={(event) => setForm({ ...form, subject: event.target.value })} required />
            <textarea className="w-full rounded-2xl border border-line bg-paper px-3 py-2 text-sm" placeholder="What they asked" value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} required />
            <button className="rounded-full bg-ink px-4 py-2 text-sm text-cream" type="submit">Log inquiry</button>
          </form>
        </Panel>
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">Messages that send themselves</p>
          <SampleNote show={triggerSample} />
          <ul className="space-y-4">
            {triggers.map((trigger) => (
              <li key={trigger.id} className="border-b border-line pb-4 last:border-0">
                <div className="flex items-center justify-between gap-3">
                  <p>{trigger.name}</p>
                  <button type="button" className="text-sm underline" onClick={() => void toggle(trigger)}>
                    {trigger.is_enabled ? "On" : "Off"}
                  </button>
                </div>
                <p className="mt-1 text-xs uppercase tracking-[0.14em] text-ink-soft">
                  {titleCase(trigger.channel)} · {titleCase(trigger.event)} · {trigger.delay_hours}h
                </p>
                <p className="mt-2 text-sm leading-6 text-ink-soft">{trigger.template_preview}</p>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
