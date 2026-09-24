# Bea Drops

Multi-tenant B2B dropshipping API for automated beauty and cosmetics stores.

## Tenancy

Shared PostgreSQL schema, not schema-per-tenant. Every store-owned row has a `tenant` foreign key. Send `X-Tenant-Slug` on store-scoped requests. The JWT authenticator resolves that header after the token is validated, because DRF authentication runs after Django middleware. Creating the first store does not require the header.

Schema-per-tenant (`django-tenants`) is the wrong default for this MVP: it fans migrations across schemas and complicates Celery before the catalog and order model have settled. Move a tenant to its own schema only if a contract requires a hard database boundary.

## Stack

Python 3.12, Django, DRF, SimpleJWT, PostgreSQL 16, Celery, Redis, Docker Compose.

## Run locally

```powershell
Copy-Item .env.example .env
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

API docs: http://localhost:8000/api/docs/

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
- `apps/orders/` customer orders, async supplier forward, fulfillment webhook
