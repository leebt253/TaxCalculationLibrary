# Tax Calculation Library

A small Python shared library for validating item records and calculating line-level and order-level tax amounts.

## Features

- Metadata-driven column mapping.
- Per-line before-tax, VAT, and after-tax calculations.
- Decimal-based monetary arithmetic.
- Two-decimal monetary output.
- Preservation of original and extra input columns.
- Fail-fast validation with structured errors.
- No database, web server, or framework required.

## Installation

From the project directory, install the package in editable mode after packaging metadata has been added:

```bash
python -m pip install -e .
```

For development and tests, install the project's development dependencies when provided by the package configuration.

## Usage

```python
from decimal import Decimal

from shared_calculation.api import calculate

records = [
    {
        "name": "Notebook",
        "count": 2,
        "price": 1500,
        "tax": Decimal("0.1"),
        "sku": "NB-001",
    }
]

metadata = {
    "has_header": True,
    "column_mapping": {
        "item_name": "name",
        "quantity": "count",
        "unit_price": "price",
        "vat_rate": "tax",
    },
}

result = calculate(records, metadata)

item = result.items[0]
assert item.original_data["sku"] == "NB-001"
assert item.before_tax == Decimal("3000.00")
assert item.after_tax == Decimal("3300.00")
assert result.total_before_tax == Decimal("3000.00")
assert result.total_after_tax == Decimal("3300.00")
```

`vat_rate` is a ratio: `Decimal("0.1")` means 10%. Required fields are `item_name`, `quantity`, `unit_price`, and `vat_rate`. Quantity and unit price must be positive integers; VAT must be between `0` and `1`, inclusive.

## Behavior

Each row is calculated independently. Rows with the same item name are not aggregated. All source fields, including fields not listed in `column_mapping`, are retained in `original_data`.

Invalid metadata or data raises a structured validation exception. The library fails fast and does not silently skip invalid rows.

Monetary line values are rounded to two decimal places using the documented V1 `Decimal` rounding policy before totals are calculated.

## Project Layout

```text
shared_calculation/
├── api.py
├── models.py
├── validation.py
├── calculation.py
├── exceptions.py
├── adapters.py
└── tests/
```

## Testing

Run the test suite with:

```bash
python -m pytest
```

The test suite should cover calculations, mappings, preservation of extra fields, boundary VAT rates, rounding, and structured validation failures.

## Scope

This V1 library intentionally excludes database persistence, web APIs, UI, currency conversion, advanced exports, duplicate aggregation, refunds, and negative quantities or prices. See [specification.md](specification.md) for the complete contract and [recommendation.md](recommendation.md) for the implementation approach.
