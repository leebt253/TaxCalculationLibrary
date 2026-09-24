"""Validation and normalization for calculation inputs."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from .exceptions import ValidationError

REQUIRED_FIELDS = ("item_name", "quantity", "unit_price", "vat_rate")


def validate_metadata(metadata: Mapping[str, Any]) -> dict[str, str]:
    """Validate metadata and return the required logical-to-physical mapping."""
    if not isinstance(metadata, Mapping):
        raise ValidationError(
            row=None,
            field=None,
            value=metadata,
            code="invalid_metadata",
            message="metadata must be a mapping",
        )

    mapping = metadata.get("column_mapping")
    if not isinstance(mapping, Mapping):
        raise ValidationError(
            row=None,
            field="column_mapping",
            value=mapping,
            code="missing_column_mapping",
            message="metadata.column_mapping must be a mapping",
        )

    validated: dict[str, str] = {}
    for logical_field in REQUIRED_FIELDS:
        physical_field = mapping.get(logical_field)
        if not isinstance(physical_field, str) or not physical_field:
            raise ValidationError(
                row=None,
                field=logical_field,
                value=physical_field,
                code="missing_required_mapping",
                message=f"column mapping for '{logical_field}' is required",
            )
        validated[logical_field] = physical_field

    return validated


def validate_and_normalize_record(
    record: Mapping[str, Any],
    mapping: Mapping[str, str],
    row: int,
) -> tuple[dict[str, Any], str, int, int, Decimal]:
    """Validate a record and return its copy plus normalized calculation values."""
    if not isinstance(record, Mapping):
        raise ValidationError(
            row=row,
            field=None,
            value=record,
            code="invalid_record",
            message="record must be a mapping",
        )

    original_data = dict(record)
    values: dict[str, Any] = {}
    for logical_field, physical_field in mapping.items():
        if physical_field not in record:
            raise ValidationError(
                row=row,
                field=logical_field,
                value=None,
                code="missing_required_field",
                message=f"required field '{physical_field}' is missing",
            )
        values[logical_field] = record[physical_field]

    item_name = values["item_name"]
    if not isinstance(item_name, str) or not item_name.strip():
        raise ValidationError(
            row=row,
            field="item_name",
            value=item_name,
            code="invalid_item_name",
            message="item_name must be a non-empty string",
        )

    quantity = _positive_integer(values["quantity"], row, "quantity")
    unit_price = _positive_integer(values["unit_price"], row, "unit_price")
    vat_rate = _vat_rate(values["vat_rate"], row)
    return original_data, item_name, quantity, unit_price, vat_rate


def _positive_integer(value: Any, row: int, field: str) -> int:
    if isinstance(value, bool):
        _raise_invalid_value(row, field, value, "invalid_integer", f"{field} must be a positive integer")
    try:
        normalized = int(value) if isinstance(value, str) else value
    except (TypeError, ValueError):
        normalized = None
    if not isinstance(normalized, int) or normalized <= 0:
        _raise_invalid_value(row, field, value, "invalid_integer", f"{field} must be a positive integer")
    return normalized


def _vat_rate(value: Any, row: int) -> Decimal:
    if isinstance(value, float):
        _raise_invalid_value(row, "vat_rate", value, "invalid_decimal", "vat_rate must use Decimal-compatible input")
    try:
        normalized = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        _raise_invalid_value(row, "vat_rate", value, "invalid_decimal", "vat_rate must be a Decimal")
    if not normalized.is_finite() or not Decimal("0") <= normalized <= Decimal("1"):
        _raise_invalid_value(row, "vat_rate", value, "vat_rate_out_of_range", "vat_rate must be between 0 and 1")
    return normalized


def _raise_invalid_value(row: int, field: str, value: Any, code: str, message: str) -> None:
    raise ValidationError(row=row, field=field, value=value, code=code, message=message)
