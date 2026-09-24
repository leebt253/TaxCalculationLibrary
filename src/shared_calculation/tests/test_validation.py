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


@pytest.mark.parametrize("metadata", [None, [], "metadata"])
def test_metadata_must_be_a_mapping(metadata):
    with pytest.raises(ValidationError) as error:
        validate_metadata(metadata)

    assert error.value.code == "invalid_metadata"
    assert error.value.row is None
    assert error.value.field is None
    assert error.value.value == metadata


def test_metadata_requires_column_mapping():
    with pytest.raises(ValidationError) as error:
        validate_metadata({})

    assert error.value.code == "missing_column_mapping"
    assert error.value.field == "column_mapping"


@pytest.mark.parametrize("logical_field", ["item_name", "quantity", "unit_price", "vat_rate"])
@pytest.mark.parametrize("physical_field", [None, "", 1])
def test_metadata_requires_non_empty_string_mapping(logical_field, physical_field):
    mapping = dict(MAPPING)
    mapping[logical_field] = physical_field

    with pytest.raises(ValidationError) as error:
        validate_metadata({"column_mapping": mapping})

    assert error.value.code == "missing_required_mapping"
    assert error.value.field == logical_field
    assert error.value.value == physical_field


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


@pytest.mark.parametrize("record", [None, [], "record"])
def test_record_must_be_a_mapping(record):
    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 3)

    assert error.value.code == "invalid_record"
    assert error.value.row == 3
    assert error.value.field is None
    assert error.value.value == record


@pytest.mark.parametrize("logical_field", ["item_name", "quantity", "unit_price", "vat_rate"])
def test_record_requires_all_mapped_fields(logical_field):
    physical_field = MAPPING[logical_field]
    record = {"name": "Notebook", "count": 1, "price": 100, "tax": Decimal("0.1")}
    del record[physical_field]

    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 2)

    assert error.value.code == "missing_required_field"
    assert error.value.row == 2
    assert error.value.field == logical_field
    assert error.value.value is None


@pytest.mark.parametrize("item_name", [None, 1, "", "   "])
def test_item_name_must_be_a_non_empty_string(item_name):
    record = {"name": item_name, "count": 1, "price": 100, "tax": Decimal("0.1")}

    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 0)

    assert error.value.code == "invalid_item_name"
    assert error.value.field == "item_name"
    assert error.value.value == item_name


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


@pytest.mark.parametrize("field", ["quantity", "unit_price"])
@pytest.mark.parametrize("value", [True, False, "not-an-int", object(), 1.5])
def test_quantity_and_price_require_positive_integers(field, value):
    record = {"name": "Notebook", "count": 1, "price": 100, "tax": Decimal("0.1")}
    record["count" if field == "quantity" else "price"] = value

    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 1)

    assert error.value.code == "invalid_integer"
    assert error.value.field == field
    assert error.value.value == value


@pytest.mark.parametrize("value", [0, 1, "0", "1"])
def test_vat_rate_accepts_inclusive_boundaries(value):
    record = {"name": "Notebook", "count": 1, "price": 100, "tax": value}

    _, _, _, _, vat_rate = validate_and_normalize_record(record, MAPPING, 0)

    assert vat_rate in (Decimal("0"), Decimal("1"))


@pytest.mark.parametrize("value", [0.1, "not-a-decimal", object(), Decimal("NaN"), Decimal("Infinity")])
def test_invalid_vat_rate_uses_structured_error(value):
    record = {"name": "Notebook", "count": 1, "price": 100, "tax": value}

    with pytest.raises(ValidationError) as error:
        validate_and_normalize_record(record, MAPPING, 0)

    assert error.value.field == "vat_rate"
    assert error.value.value is value
    assert error.value.code in {"invalid_decimal", "vat_rate_out_of_range"}
