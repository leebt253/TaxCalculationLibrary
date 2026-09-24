"""Pure Decimal-based tax calculations."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")


def calculate_line(quantity: int, unit_price: int, vat_rate: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Calculate rounded before-tax, VAT, and after-tax line values."""
    before_tax = (Decimal(quantity) * Decimal(unit_price)).quantize(
        MONEY_QUANTUM, rounding=ROUND_HALF_UP
    )
    vat = (before_tax * vat_rate).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    after_tax = (before_tax + vat).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    return before_tax, vat, after_tax
