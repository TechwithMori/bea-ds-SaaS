export type User = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name: string;
};

export type Tenant = {
  id: string;
  name: string;
  slug: string;
  status: string;
  plan: string;
  currency: string;
  niche: string;
  is_default: boolean;
  custom_domain: string;
};

export type SupplierSync = {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
  sync_status: string;
  last_synced_at: string | null;
};

export type CatalogRow = {
  id: string;
  title: string;
  sku: string;
  category: string;
  brand: string;
  wholesale_price: string;
  suggested_retail_price: string;
  margin_percent: string;
  stock_level: number;
  compliance_status: string;
  compliance_notes: string;
  ingredients: string[];
  supplier_name: string;
  sync_status: string;
};

export type ListingRow = {
  id: string;
  title: string;
  variant_name: string;
  sku: string;
  category: string;
  wholesale_price: string;
  retail_price: string;
  margin_percent: string;
  stock_level: number;
  is_published: boolean;
  compliance_status: string;
  supplier_name: string;
  sync_status: string;
};

export type SourcingOverview = {
  suppliers: SupplierSync[];
  compliance: { compliant: number; pending_review: number; restricted: number };
  catalog: CatalogRow[];
  listings: ListingRow[];
};

export type ContentAsset = {
  id: string;
  title: string;
  kind: string;
  status: string;
  channel: string;
  body: string;
  asset_url: string;
  created_at?: string;
};

export type MarketingHook = {
  id: string;
  headline: string;
  angle: string;
  platform: string;
  status: string;
};

export type ChannelIntegration = {
  id: string;
  provider: string;
  status: string;
  account_label: string;
};

export type StorefrontConfig = {
  id: string;
  theme: string;
  font_pairing: string;
  primary_color: string;
  accent_color: string;
  announcement: string;
  show_reviews: boolean;
  show_urgency: boolean;
  show_bundles: boolean;
  free_shipping_threshold: string;
};

export type BundleItem = {
  id: string;
  store_product: string;
  quantity: number;
  title: string;
};

export type Bundle = {
  id: string;
  name: string;
  description: string;
  discount_percent: string;
  is_active: boolean;
  items: BundleItem[];
};

export type OrderRecord = {
  id: string;
  number: string;
  status: string;
  customer_name: string;
  customer_email: string;
  shipping_address: { country?: string; city?: string; line1?: string };
  currency: string;
  total: string;
  tracking_carrier: string;
  tracking_number: string;
  route_name: string;
  route_carrier: string;
  created_at: string;
};

export type OrderSummary = {
  pending: number;
  processing: number;
  shipped: number;
  exceptions: number;
};

export type ShippingRoute = {
  id: string;
  name: string;
  carrier: string;
  service_level: string;
  regions: string[];
  priority: number;
  is_active: boolean;
};

export type CustomerRecord = {
  id: string;
  name: string;
  email: string;
  loyalty_tier: string;
  lifetime_value: string;
  orders_count: number;
  points: number;
  last_order_at: string | null;
};

export type Inquiry = {
  id: string;
  customer_name: string;
  customer_email: string;
  subject: string;
  body: string;
  status: string;
  channel: string;
  created_at?: string;
};

export type RetentionTrigger = {
  id: string;
  name: string;
  channel: string;
  event: string;
  is_enabled: boolean;
  delay_hours: number;
  template_preview: string;
};

export type AnalyticsPoint = { day: string; revenue: string; orders: number };

export type AnalyticsOverview = {
  currency: string;
  days: number;
  revenue: string;
  order_count: number;
  aov: string;
  cogs: string;
  ad_spend: string;
  gross_profit: string;
  net_profit: string;
  net_margin_percent: string;
  cac: string | null;
  new_customers: number;
  series: AnalyticsPoint[];
  spend_by_channel: { channel: string; amount: string }[];
  top_products: { title: string; revenue: string; units: number }[];
};
