import type {
  AnalyticsOverview,
  Bundle,
  ChannelIntegration,
  ContentAsset,
  CustomerRecord,
  Inquiry,
  ListingRow,
  MarketingHook,
  OrderRecord,
  OrderSummary,
  RetentionTrigger,
  ShippingRoute,
  SourcingOverview,
  StorefrontConfig,
} from "../api/types";

export const sampleSourcing: SourcingOverview = {
  suppliers: [
    {
      id: "sup-north",
      name: "North Glow Labs",
      code: "north-glow",
      is_active: true,
      sync_status: "ok",
      last_synced_at: "2026-10-05T08:10:00Z",
    },
    {
      id: "sup-atelier",
      name: "Atelier Pigment",
      code: "atelier-pigment",
      is_active: true,
      sync_status: "failed",
      last_synced_at: "2026-10-04T19:02:00Z",
    },
  ],
  compliance: { compliant: 3, pending_review: 1, restricted: 1 },
  catalog: [
    row("Calm Repair Serum", "BEA-SERUM-01", "skincare", "42.00", "78.00", "46.2", 240, "compliant", "", ["niacinamide", "panthenol"], "North Glow Labs", "ok"),
    row("Barrier Cream", "BEA-CREAM-02", "skincare", "28.00", "54.00", "48.1", 180, "compliant", "", ["ceramides", "squalane"], "North Glow Labs", "ok"),
    row("Night Oil", "BEA-OIL-03", "skincare", "31.00", "64.00", "51.6", 40, "pending_review", "Fragrance allergen check open.", ["squalane", "rosehip"], "North Glow Labs", "ok"),
    row("Soft Lip Tint", "BEA-LIP-04", "makeup", "9.50", "24.00", "60.4", 320, "compliant", "", ["castor oil"], "Atelier Pigment", "failed"),
    row("Gel Cleanser", "BEA-WASH-05", "skincare", "11.00", "28.00", "60.7", 0, "restricted", "Preservative system under review.", ["glycerin"], "North Glow Labs", "ok"),
  ],
  listings: [
    listing("Calm Repair Serum", "30 ml", "BEA-SERUM-01-30", "42.00", "78.00", "46.2", 240, true, "compliant", "North Glow Labs", "ok"),
    listing("Barrier Cream", "50 ml", "BEA-CREAM-02-50", "28.00", "54.00", "48.1", 180, true, "compliant", "North Glow Labs", "ok"),
    listing("Night Oil", "30 ml", "BEA-OIL-03-30", "31.00", "64.00", "51.6", 40, false, "pending_review", "North Glow Labs", "ok"),
  ],
};

function row(
  title: string,
  sku: string,
  category: string,
  wholesale: string,
  retail: string,
  margin: string,
  stock: number,
  compliance: string,
  notes: string,
  ingredients: string[],
  supplier: string,
  sync: string,
): SourcingOverview["catalog"][number] {
  return {
    id: sku,
    title,
    sku,
    category,
    brand: "North Glow",
    wholesale_price: wholesale,
    suggested_retail_price: retail,
    margin_percent: margin,
    stock_level: stock,
    compliance_status: compliance,
    compliance_notes: notes,
    ingredients,
    supplier_name: supplier,
    sync_status: sync,
  };
}

function listing(
  title: string,
  variant: string,
  sku: string,
  wholesale: string,
  retail: string,
  margin: string,
  stock: number,
  published: boolean,
  compliance: string,
  supplier: string,
  sync: string,
): ListingRow {
  return {
    id: sku,
    title,
    variant_name: variant,
    sku,
    category: "skincare",
    wholesale_price: wholesale,
    retail_price: retail,
    margin_percent: margin,
    stock_level: stock,
    is_published: published,
    compliance_status: compliance,
    supplier_name: supplier,
    sync_status: sync,
  };
}

export const sampleAssets: ContentAsset[] = [
  {
    id: "asset-1",
    title: "PDP hero — morning serum",
    kind: "image",
    status: "draft",
    channel: "storefront",
    body: "Close crop on glass, warm stone, one drop on the back of the hand.",
    asset_url: "",
  },
  {
    id: "asset-2",
    title: "UGC caption set",
    kind: "copy",
    status: "approved",
    channel: "tiktok",
    body: "I replaced four bottles with this. Skin feels calm by Thursday.",
    asset_url: "",
  },
];

export const sampleHooks: MarketingHook[] = [
  { id: "hook-1", headline: "Your barrier cream, without the twelve-step lecture.", angle: "routine", platform: "instagram", status: "ready" },
  { id: "hook-2", headline: "Three textures. One evening sink. Zero guesswork.", angle: "bundle", platform: "tiktok", status: "draft" },
  { id: "hook-3", headline: "The serum people finish — then write us about.", angle: "social proof", platform: "email", status: "draft" },
];

export const sampleIntegrations: ChannelIntegration[] = [
  { id: "ch-ig", provider: "instagram", status: "connected", account_label: "Lumen Atelier" },
  { id: "ch-tt", provider: "tiktok", status: "disconnected", account_label: "" },
  { id: "ch-meta", provider: "meta_ads", status: "connected", account_label: "Prospecting — serum" },
  { id: "ch-google", provider: "google_ads", status: "disconnected", account_label: "" },
  { id: "ch-pin", provider: "pinterest", status: "disconnected", account_label: "" },
  { id: "ch-kl", provider: "klaviyo", status: "connected", account_label: "Care flows" },
];

export const sampleStorefront: StorefrontConfig = {
  id: "sf-1",
  theme: "atelier",
  font_pairing: "editorial",
  primary_color: "#241910",
  accent_color: "#C9847A",
  announcement: "Complimentary samples on orders over $75.",
  show_reviews: true,
  show_urgency: false,
  show_bundles: true,
  free_shipping_threshold: "75.00",
};

export const sampleBundles: Bundle[] = [
  {
    id: "bundle-1",
    name: "Evening Sink Set",
    description: "Serum and barrier cream, sequenced for the last ten minutes of the day.",
    discount_percent: "12.00",
    is_active: true,
    items: [
      { id: "bi-1", store_product: "BEA-SERUM-01-30", quantity: 1, title: "Calm Repair Serum" },
      { id: "bi-2", store_product: "BEA-CREAM-02-50", quantity: 1, title: "Barrier Cream" },
    ],
  },
];

export const sampleSummary: OrderSummary = { pending: 1, processing: 2, shipped: 1, exceptions: 0 };

export const sampleOrders: OrderRecord[] = [
  order("BD-LUMEN-000004", "fulfilled", "Mara Ellison", "mara@example.com", "US", "84.00", "United States", "USPS", "TRK000004"),
  order("BD-LUMEN-000003", "forwarded", "Jonah Park", "jonah@example.com", "US", "60.00", "United States", "USPS", ""),
  order("BD-LUMEN-000002", "paid", "Adele Costa", "adele@example.com", "FR", "54.00", "European Union", "DHL", ""),
  order("BD-LUMEN-000001", "pending", "Noah Idris", "noah@example.com", "DE", "60.00", "European Union", "DHL", ""),
];

function order(
  number: string,
  status: string,
  name: string,
  email: string,
  country: string,
  total: string,
  route: string,
  carrier: string,
  tracking: string,
): OrderRecord {
  return {
    id: number,
    number,
    status,
    customer_name: name,
    customer_email: email,
    shipping_address: { country, city: "—", line1: "" },
    currency: "USD",
    total,
    tracking_carrier: tracking ? carrier : "",
    tracking_number: tracking,
    route_name: route,
    route_carrier: carrier,
    created_at: "2026-10-03T15:00:00Z",
  };
}

export const sampleRoutes: ShippingRoute[] = [
  { id: "rt-us", name: "United States", carrier: "USPS", service_level: "standard", regions: ["US"], priority: 10, is_active: true },
  { id: "rt-eu", name: "European Union", carrier: "DHL", service_level: "express", regions: ["EU"], priority: 20, is_active: true },
  { id: "rt-row", name: "Rest of world", carrier: "DHL", service_level: "standard", regions: ["ROW"], priority: 30, is_active: true },
];

export const sampleCustomers: CustomerRecord[] = [
  { id: "cu-1", name: "Mara Ellison", email: "mara@example.com", loyalty_tier: "insider", lifetime_value: "162.00", orders_count: 2, points: 162, last_order_at: "2026-10-04T12:00:00Z" },
  { id: "cu-2", name: "Jonah Park", email: "jonah@example.com", loyalty_tier: "member", lifetime_value: "60.00", orders_count: 1, points: 60, last_order_at: "2026-10-03T12:00:00Z" },
  { id: "cu-3", name: "Adele Costa", email: "adele@example.com", loyalty_tier: "muse", lifetime_value: "348.00", orders_count: 4, points: 348, last_order_at: "2026-10-02T12:00:00Z" },
];

export const sampleInquiries: Inquiry[] = [
  { id: "inq-1", customer_name: "Mara Ellison", customer_email: "mara@example.com", subject: "Is the serum fragrance-free?", body: "I want Calm Repair Serum but I react to added scent.", status: "open", channel: "email" },
  { id: "inq-2", customer_name: "Jonah Park", customer_email: "jonah@example.com", subject: "Tracking page is empty", body: "The shipping mail arrived, but the carrier page is blank.", status: "waiting", channel: "chat" },
];

export const sampleTriggers: RetentionTrigger[] = [
  { id: "tr-1", name: "Welcome to the ritual", channel: "email", event: "welcome", is_enabled: true, delay_hours: 0, template_preview: "Thanks for joining. Here is how to start the first seven days." },
  { id: "tr-2", name: "Abandoned ritual", channel: "email", event: "abandoned_checkout", is_enabled: true, delay_hours: 2, template_preview: "Your routine is still waiting at the sink." },
  { id: "tr-3", name: "Post-purchase care", channel: "sms", event: "post_purchase", is_enabled: true, delay_hours: 24, template_preview: "Your order is moving. Patch-test the serum the first night." },
  { id: "tr-4", name: "Win-back", channel: "email", event: "winback", is_enabled: false, delay_hours: 720, template_preview: "It has been a while. Your insider points are still here." },
];

export const sampleAnalytics: AnalyticsOverview = {
  currency: "USD",
  days: 30,
  revenue: "12840.00",
  order_count: 46,
  aov: "279.13",
  cogs: "4820.00",
  ad_spend: "1960.00",
  gross_profit: "8020.00",
  net_profit: "6060.00",
  net_margin_percent: "47.2",
  cac: "32.13",
  new_customers: 61,
  series: [420, 680, 510, 890, 740, 960, 610, 880, 1020, 760, 940, 870, 1100, 980].map((revenue, index) => ({
    day: `2026-09-${String(index + 16).padStart(2, "0")}`,
    revenue: revenue.toFixed(2),
    orders: Math.max(1, Math.round(revenue / 280)),
  })),
  spend_by_channel: [
    { channel: "meta_ads", amount: "980.00" },
    { channel: "tiktok", amount: "640.00" },
    { channel: "google_ads", amount: "340.00" },
  ],
  top_products: [
    { title: "Calm Repair Serum", revenue: "5460.00", units: 70 },
    { title: "Barrier Cream", revenue: "3240.00", units: 60 },
    { title: "Night Oil", revenue: "1920.00", units: 30 },
  ],
};
