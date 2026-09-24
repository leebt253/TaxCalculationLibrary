from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


def _to_decimal(value: Any, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"'{field_name}' must be a valid numeric value.") from exc


def validate_item_record(item: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise ValueError("Item must be a mapping.")

    required_fields = ("sku", "quantity", "unit_price")
    missing_fields = [field for field in required_fields if field not in item]
    if missing_fields:
        raise ValueError(
            f"Item is missing required field(s): {', '.join(missing_fields)}."
        )

    sku = item["sku"]
    if not isinstance(sku, str) or not sku.strip():
        raise ValueError("'sku' must be a non-empty string.")

    quantity = item["quantity"]
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("'quantity' must be a positive integer.")

    unit_price = _to_decimal(item["unit_price"], "unit_price")
    if unit_price < Decimal("0"):
        raise ValueError("'unit_price' must be greater than or equal to 0.")

    tax_exempt = item.get("tax_exempt", False)
    if not isinstance(tax_exempt, bool):
        raise ValueError("'tax_exempt' must be a boolean when provided.")

    return {
        "sku": sku.strip(),
        "quantity": quantity,
        "unit_price": unit_price,
        "tax_exempt": tax_exempt,
    }
