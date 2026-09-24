"""Tenant context is resolved in JWT authentication, not middleware.

DRF authenticates after Django middleware, so a middleware that reads
``request.user`` cannot see a Bearer token. See
``apps.tenants.authentication.TenantJWTAuthentication``.
"""
