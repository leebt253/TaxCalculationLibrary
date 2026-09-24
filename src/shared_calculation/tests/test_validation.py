from decimal import Decimal

import pytest

from shared_calculation.exceptions import ValidationError
from shared_calculation.validation import validate_and_normalize_record, validate_metadata


MAPPING = {
    "item_name": "name",
    "quantity": "count",
    "unit_price": "price",
    "vat_rate": "tax",
}


def test_metadata_requires_all_logical_fields():
    with pytest.raises(ValidationError) as error:
        validate_metadata({"column_mapping": {"item_name": "name"}})

    assert error.value.code == "missing_required_mapping"
    assert error.value.field == "quantity"


def test_record_preserves_extra_columns_and_normalizes_values():
    original, item_name, quantity, unit_price, vat_rate = validate_and_normalize_record(
        {"name": "Notebook", "count": "2", "price": 1500, "tax": "0.1", "sku": "NB-1"},
        MAPPING,
        0,
    )

    assert original["sku"] == "NB-1"
    assert item_name == "Notebook"
    assert quantity == 2
    assert unit_price == 1500
    assert vat_rate == Decimal("0.1")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("quantity", 0, "invalid_integer"),
        ("unit_price", -1, "invalid_integer"),
        ("vat_rate", Decimal("-0.01"), "vat_rate_out_of_range"),
        ("vat_rate", Decimal("1.01"), "vat_rate_out_of_range"),
    ],
)
def test_invalid_values_fail_fast(field, value, code):
    record = {"name": "Notebook", "count": 1, "price": 100, "tax": Decimal("0.1")}
    record[{"quantity": "count", "unit_price": "price", "vat_rate": "tax"}.get(field, field)] = value

    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 4)

    assert error.value.row == 4
    assert error.value.field == field
    assert error.value.code == code
