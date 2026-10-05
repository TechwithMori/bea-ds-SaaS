import type { Lang } from "../i18n/LanguageContext";

const localeFor = (lang: Lang) => (lang === "fa" ? "fa-IR" : "en-US");

export function formatNumber(value: string | number, lang: Lang, fractionDigits = 0) {
  const amount = Number(value);
  if (Number.isNaN(amount)) return "—";
  return new Intl.NumberFormat(localeFor(lang), {
    numberingSystem: lang === "fa" ? "arabext" : "latn",
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(amount);
}

export function money(value: string | number | null | undefined, currency = "USD", lang: Lang = "fa") {
  if (value === null || value === undefined || value === "") return "—";
  const amount = Number(value);
  if (Number.isNaN(amount)) return "—";
  const code = currency.toUpperCase();
  if (code === "IRT") {
    const formatted = formatNumber(amount, lang, 0);
    return lang === "fa" ? `${formatted} تومان` : `${formatted} IRT`;
  }
  if (code === "IRR") {
    const formatted = formatNumber(amount, lang, 0);
    return lang === "fa" ? `${formatted} ریال` : `${formatted} IRR`;
  }
  return new Intl.NumberFormat(localeFor(lang), {
    style: "currency",
    currency: code,
    numberingSystem: lang === "fa" ? "arabext" : "latn",
  }).format(amount);
}

export function percent(value: string | number, lang: Lang) {
  const amount = Number(value);
  const digits = Number.isInteger(amount) ? 0 : 1;
  const mark = lang === "fa" ? "٪" : "%";
  return `${formatNumber(amount, lang, digits)}${mark}`;
}

export function laneFor(status: string) {
  if (status === "pending") return "pending";
  if (status === "paid" || status === "forwarded") return "processing";
  if (status === "fulfilled") return "shipped";
  return "exceptions";
}
