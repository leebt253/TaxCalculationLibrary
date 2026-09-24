"""Pure Decimal-based tax calculations."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")


def normalize_money(value: Decimal) -> Decimal:
    """Remove insignificant trailing zeroes without using scientific notation."""
    if value == value.to_integral_value():
        return value.quantize(Decimal("1"))
    return value.normalize()


def calculate_line(quantity: int, unit_price: int, vat_rate: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Calculate rounded before-tax, VAT, and after-tax line values."""
    before_tax = (Decimal(quantity) * Decimal(unit_price)).quantize(
        MONEY_QUANTUM, rounding=ROUND_HALF_UP
    )
    vat = (before_tax * vat_rate).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    after_tax = (before_tax + vat).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
    return tuple(normalize_money(value) for value in (before_tax, vat, after_tax))
