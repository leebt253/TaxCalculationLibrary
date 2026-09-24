"""Domain models for shared tax calculations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping


@dataclass(frozen=True)
class CalculationItem:
    """Tax calculation for one input record."""

    original_data: Mapping[str, Any]
    before_tax: Decimal
    vat: Decimal
    after_tax: Decimal


@dataclass(frozen=True)
class CalculationResult:
    """Line results and order totals."""

    items: list[CalculationItem]
    total_before_tax: Decimal
    total_after_tax: Decimal
