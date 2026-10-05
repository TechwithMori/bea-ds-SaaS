export function money(value: string | number | null | undefined, currency = "USD") {
  if (value === null || value === undefined || value === "") return "—";
  const amount = Number(value);
  if (Number.isNaN(amount)) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
}

export function titleCase(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function laneFor(status: string) {
  if (status === "pending") return "pending";
  if (status === "paid" || status === "forwarded") return "processing";
  if (status === "fulfilled") return "shipped";
  return "exceptions";
}
