"""Public API for shared tax calculations."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Mapping

from .calculation import calculate_line, normalize_money
from .models import CalculationItem, CalculationResult
from .validation import validate_and_normalize_record, validate_metadata


def calculate(data: Iterable[Mapping[str, Any]], metadata: Mapping[str, Any]) -> CalculationResult:
    """Validate records and return line-level and order-level tax results."""
    mapping = validate_metadata(metadata)
    items: list[CalculationItem] = []
    total_before_tax = Decimal("0.00")
    total_after_tax = Decimal("0.00")

    for row, record in enumerate(data):
        original_data, _, quantity, unit_price, vat_rate = validate_and_normalize_record(
            record, mapping, row
        )
        before_tax, vat, after_tax = calculate_line(quantity, unit_price, vat_rate)
        items.append(
            CalculationItem(
                original_data=original_data,
                before_tax=before_tax,
                vat=vat,
                after_tax=after_tax,
            )
        )
        total_before_tax += before_tax
        total_after_tax += after_tax

    return CalculationResult(
        items=items,
        total_before_tax=normalize_money(total_before_tax.quantize(Decimal("0.01"))),
        total_after_tax=normalize_money(total_after_tax.quantize(Decimal("0.01"))),
    )
