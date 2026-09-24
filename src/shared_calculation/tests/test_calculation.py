from decimal import Decimal

import pytest

from shared_calculation import calculate
from shared_calculation.exceptions import ValidationError


METADATA = {
    "has_header": True,
    "column_mapping": {
        "item_name": "name",
        "quantity": "count",
        "unit_price": "price",
        "vat_rate": "tax",
    },
}


def test_calculates_lines_and_totals_with_extra_columns():
    result = calculate(
        [
            {"name": "Notebook", "count": 2, "price": 1500, "tax": Decimal("0.1"), "sku": "NB-1"},
            {"name": "Pen", "count": 3, "price": 100, "tax": Decimal("0"), "sku": "P-1"},
        ],
        METADATA,
    )

    assert result.items[0].before_tax == Decimal("3000.00")
    assert result.items[0].vat == Decimal("300.00")
    assert result.items[0].after_tax == Decimal("3300.00")
    assert result.items[0].original_data["sku"] == "NB-1"
    assert result.total_before_tax == Decimal("3300.00")
    assert result.total_after_tax == Decimal("3600.00")


def test_duplicate_items_are_not_aggregated_and_vat_one_is_valid():
    result = calculate(
        [
            {"name": "Item", "count": 1, "price": 1, "tax": Decimal("1")},
            {"name": "Item", "count": 1, "price": 1, "tax": Decimal("1")},
        ],
        METADATA,
    )

    assert len(result.items) == 2
    assert result.total_after_tax == Decimal("4.00")


def test_rounds_each_line_before_totals():
    result = calculate(
        [
            {"name": "A", "count": 1, "price": 1, "tax": Decimal("0.005")},
            {"name": "B", "count": 1, "price": 1, "tax": Decimal("0.005")},
        ],
        METADATA,
    )

    assert [item.after_tax for item in result.items] == [Decimal("1.01"), Decimal("1.01")]
    assert result.total_after_tax == Decimal("2.02")


def test_prints_money_without_insignificant_decimal_zeroes():
    result = calculate(
        [
            {"name": "No VAT", "count": 1, "price": 1, "tax": Decimal("0")},
            {"name": "Ten Percent", "count": 1, "price": 1, "tax": Decimal("0.1")},
        ],
        METADATA,
    )

    assert str(result.items[0].before_tax) == "1"
    assert str(result.items[0].vat) == "0"
    assert str(result.items[1].vat) == "0.1"
    assert str(result.items[1].after_tax) == "1.1"


def test_empty_input_returns_empty_result_with_zero_totals():
    result = calculate([], METADATA)

    assert result.items == []
    assert result.total_before_tax == Decimal("0")
    assert result.total_after_tax == Decimal("0")


def test_invalid_row_fails_fast_with_structured_error():
    with pytest.raises(ValidationError) as error:
        calculate(
            [{"name": "Valid", "count": 1, "price": 10, "tax": Decimal("0")},
             {"name": "Invalid", "count": 0, "price": 10, "tax": Decimal("0")}],
            METADATA,
        )

    assert error.value.row == 1
    assert error.value.field == "quantity"
    assert error.value.code == "invalid_integer"
