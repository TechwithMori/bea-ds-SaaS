"""Deployment schema named from CUSTOMER_NAME.

One process uses one schema, ``{customer_name}_schema``. Store rows inside that
schema are still separated by the tenant foreign key.
"""

from __future__ import annotations

import re

from django.core.exceptions import ImproperlyConfigured

_NAME = re.compile(r"[^a-z0-9]+")


def schema_name_for_customer(customer_name: str) -> str | None:
    """Return ``acme_schema`` for ``Acme``, or None when the name is blank."""
    raw = customer_name.strip().lower()
    if not raw:
        return None
    slug = _NAME.sub("_", raw).strip("_")
    if not slug or not slug[0].isalpha():
        raise ImproperlyConfigured(
            "CUSTOMER_NAME must start with a letter. Letters, numbers, spaces, and hyphens are allowed."
        )
    return f"{slug}_schema"


def use_customer_schema(schema: str) -> None:
    """Create the schema on each new Postgres connection and select it."""
    from django.db.backends.signals import connection_created

    def prepare(sender, connection, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if connection.vendor != "postgresql":
            return
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
            cursor.execute(f'SET search_path TO "{schema}"')

    # weak=False keeps this nested receiver alive after use_customer_schema() returns.
    connection_created.connect(
        prepare,
        dispatch_uid=f"bea-customer-schema-{schema}",
        weak=False,
    )
