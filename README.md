# Bea Drops

Multi-tenant B2B dropshipping API for automated beauty and cosmetics stores.

## Tenancy

Set `CUSTOMER_NAME` for a deployment. The API then uses the Postgres schema `{customer_name}_schema` instead of `public`, and creates that schema on connect. Until the variable is set, Django stays on `public`.

Inside that schema, every store-owned row still has a `tenant` foreign key. Send `X-Tenant-Slug` on store-scoped requests. The JWT authenticator resolves that header after the token is validated, because DRF authentication runs after Django middleware. Creating the first store does not require the header. After you set `CUSTOMER_NAME`, recreate the web and worker containers and run `migrate` so tables are created in the new schema.

## Stack

Python 3.12, Django, DRF, SimpleJWT, PostgreSQL 16, Celery, Redis, Docker Compose.

## Run locally

```powershell
Copy-Item .env.example .env
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

API docs: http://localhost:8010/api/docs/

The Compose web service listens on port **8010**.

## Dashboard

The operator dashboard is a Vite app in `frontend/`. It talks to the API through a dev proxy.

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Register a store, or choose **Tour the sample workspace** to walk every desk with illustrative data. To fill the API with a live demo store:

```powershell
docker compose exec web python manage.py seed_workspace
```

Sign in as `iris@lumenatelier.test` / `bea-drops-demo`.

Desk endpoints, all under `/api/v1/` and scoped with `X-Tenant-Slug` unless noted:

- Sourcing: `sourcing/overview/`, `catalog/`, `store-products/`
- Growth: `marketing/assets/`, `marketing/hooks/`, `marketing/integrations/`, `marketing/spend/`
- Shop: `storefront/config/`, `storefront/bundles/`
- Logistics: `orders/`, `orders/summary/`, `shipping-routes/`
- Retention: `customers/`, `inquiries/`, `retention-triggers/`
- Finance: `analytics/overview/?days=30`

## First requests

1. `POST /api/v1/auth/register/` with `email` and `password`.
2. `POST /api/v1/auth/token/` to obtain a JWT.
3. `POST /api/v1/tenants/` with `Authorization: Bearer <access>` and `{"name": "Glow Lab"}`.
4. Subsequent catalog listings and orders use `X-Tenant-Slug: glow-lab`.

## Layout

- `core/` settings, WSGI/ASGI, Celery, root URLs
- `apps/authentication/` email user and JWT
- `apps/tenants/` store instances, middleware, membership permission
- `apps/products/` global supplier catalog plus per-store listings
- `apps/orders/` customer orders, shipping lanes, async supplier forward, fulfillment webhook
- `apps/marketing/` creative assets, hooks, channel connections, ad spend
- `apps/storefront/` theme, conversion settings, bundles
- `apps/customers/` buyers, inquiries, retention triggers
- `apps/analytics/` revenue, AOV, CAC, and margin
- `frontend/` React operator dashboard
