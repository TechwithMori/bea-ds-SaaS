"""Small money helpers shared by read APIs."""

from __future__ import annotations

from decimal import Decimal


def money(value: Decimal | int | str | None) -> str:
    amount = Decimal(value or 0).quantize(Decimal("0.01"))
    return f"{amount:.2f}"


def margin_percent(retail: Decimal | None, cost: Decimal | None) -> str:
    price = Decimal(retail or 0)
    if price <= 0:
        return "0.0"
    ratio = (price - Decimal(cost or 0)) / price * Decimal(100)
    return f"{ratio.quantize(Decimal('0.1'))}"
