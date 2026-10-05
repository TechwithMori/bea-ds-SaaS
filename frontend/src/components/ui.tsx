import type { ReactNode } from "react";
import { useI18n } from "../i18n/LanguageContext";

export function PageHeader({ desk, title, lede }: { desk: string; title: string; lede: string }) {
  return (
    <header className="mb-8 max-w-2xl">
      <p className="text-[11px] uppercase tracking-[0.22em] text-blush">{desk}</p>
      <h1 className="mt-2 font-display text-4xl text-ink md:text-5xl">{title}</h1>
      <p className="mt-3 text-sm leading-6 text-ink-soft">{lede}</p>
    </header>
  );
}

export function SampleNote({ show, children }: { show: boolean; children?: ReactNode }) {
  const { t } = useI18n();
  if (!show) return null;
  return (
    <p className="mb-6 rounded-full border border-gold/30 bg-[#f6efe2] px-4 py-2 text-sm text-ink">
      {children ?? t("sampleFigures")}
    </p>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-3xl border border-line bg-cream p-5 shadow-card ${className}`}>{children}</section>;
}

export function Stat({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <Panel>
      <p className="text-[11px] uppercase tracking-[0.18em] text-ink-soft">{label}</p>
      <p className="mt-3 font-display text-3xl text-ink">{value}</p>
      {detail ? <p className="mt-2 text-sm text-ink-soft">{detail}</p> : null}
    </Panel>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "good" | "warn" | "bad" }) {
  const tones = {
    neutral: "bg-mist text-ink",
    good: "bg-[#e5f2ec] text-moss",
    warn: "bg-[#f8efd8] text-[#8a6232]",
    bad: "bg-[#f8e4df] text-[#8d3d32]",
  };
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs ${tones[tone]}`}>{children}</span>;
}

export function toneFor(status: string): "neutral" | "good" | "warn" | "bad" {
  if (["ok", "compliant", "connected", "live", "ready", "fulfilled", "shipped", "active", "resolved", "muse"].includes(status)) {
    return "good";
  }
  if (["pending", "pending_review", "waiting", "paid", "forwarded", "processing", "draft", "approved"].includes(status)) {
    return "warn";
  }
  if (["failed", "restricted", "error", "cancelled", "exceptions"].includes(status)) return "bad";
  return "neutral";
}
