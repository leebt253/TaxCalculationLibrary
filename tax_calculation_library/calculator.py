from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Mapping

from .validation import validate_item_record

MONEY_QUANT = Decimal("0.01")


def _to_rate_decimal(tax_rate: Any) -> Decimal:
    try:
        rate = Decimal(str(tax_rate))
    except Exception as exc:  # pragma: no cover - broad for strict conversion
        raise ValueError("'tax_rate' must be a valid numeric value.") from exc

    if rate < Decimal("0"):
        raise ValueError("'tax_rate' must be greater than or equal to 0.")
    return rate


def calculate_line_tax(item: Mapping[str, Any], tax_rate: Any) -> dict[str, Any]:
    validated = validate_item_record(item)
    rate = _to_rate_decimal(tax_rate)

    line_subtotal = (validated["unit_price"] * validated["quantity"]).quantize(
        MONEY_QUANT, rounding=ROUND_HALF_UP
    )
    line_tax = Decimal("0.00")
    if not validated["tax_exempt"]:
        line_tax = (line_subtotal * rate).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    line_total = (line_subtotal + line_tax).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

    return {
        **validated,
        "line_subtotal": line_subtotal,
        "line_tax": line_tax,
        "line_total": line_total,
    }


def calculate_order_tax(
    items: Iterable[Mapping[str, Any]], tax_rate: Any
) -> dict[str, Any]:
    if items is None:
        raise ValueError("'items' must be an iterable of item records.")

    lines = [calculate_line_tax(item, tax_rate) for item in items]
    order_subtotal = sum((line["line_subtotal"] for line in lines), Decimal("0.00"))
    order_tax = sum((line["line_tax"] for line in lines), Decimal("0.00"))
    order_total = (order_subtotal + order_tax).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

    return {
        "lines": lines,
        "order_subtotal": order_subtotal.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP),
        "order_tax": order_tax.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP),
        "order_total": order_total,
    }
