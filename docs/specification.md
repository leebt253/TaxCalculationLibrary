# Technical Specification: Python Shared Calculation Library

## 1. Purpose

The library calculates tax amounts for tabular item records. It validates metadata and input records, calculates each line independently, and returns structured line and order results.

The default currency is Korean Won (KRW). Currency conversion is outside the scope of V1.

## 2. Functional Scope

The library must:

- Accept records and metadata through `calculate(data, metadata)`.
- Resolve logical fields through metadata-defined column mappings.
- Validate required mappings and values.
- Calculate before-tax, VAT, and after-tax amounts for every valid row.
- Sum line results into order totals.
- Preserve the complete original input record, including unmapped columns.
- Return actionable structured errors for invalid input.

The library must not include database access, a web server, UI behavior, currency conversion, duplicate aggregation, refunds, or negative quantities/prices in V1.

## 3. Public API

```python
from shared_calculation.api import calculate

result = calculate(data, metadata)
```

`calculate` is the only required public calculation entry point. File delimiter, encoding, physical column names, and rounding configuration are not public calculation parameters; physical names are supplied through metadata.

### Input

`data` is an iterable of records. A record may be a mapping or another normalized record representation supported by the package.

`metadata` contains:

- `has_header`: whether the source includes a header.
- `column_mapping`: mapping from logical fields to physical column names.

Required logical fields:

- `item_name`
- `quantity`
- `unit_price`
- `vat_rate`

Additional source columns are allowed and must be preserved.

### Field Contract

| Logical field | Type | Constraint |
|---|---|---|
| `item_name` | `str` | Required and non-empty |
| `quantity` | `int` | Required and greater than `0` |
| `unit_price` | `int` | Required and greater than `0` |
| `vat_rate` | `Decimal` | Required and between `0` and `1`, inclusive |

The implementation may normalize compatible input representations at the boundary, but monetary and rate calculations must use `Decimal` internally. Floating-point values must not be used for money calculations.

## 4. Calculation Rules

For each input row:

```text
line_before_tax = quantity * unit_price
line_vat        = line_before_tax * vat_rate
line_after_tax  = line_before_tax + line_vat
```

The implementation must:

- Calculate rows independently.
- Keep duplicate item names as separate lines.
- Quantize line monetary values to two decimal places before adding totals.
- Use `Decimal("0.01")` and the explicitly documented V1 rounding policy `ROUND_HALF_UP`.
- Calculate order totals by summing the rounded line values.

VAT rates of `0` and `1` are valid. Negative quantities, negative prices, and VAT values outside `0..1` are invalid.

## 5. Output Contract

The result must expose:

- A list of calculation items.
- `total_before_tax`.
- `total_after_tax`.

Each calculation item must expose:

- `original_data`: the complete original record, including extra columns.
- `before_tax`.
- `after_tax`.

VAT may be exposed as an additional line field, but the required output contract includes before-tax and after-tax values. Monetary values must be `Decimal` values quantized to two decimal places.

## 6. Validation and Errors

Validation is fail-fast: the request fails when metadata or a required row is invalid. Invalid rows must never be silently skipped.

Validation must detect at least:

- Missing required mappings.
- Missing required fields in a record.
- Empty or invalid item names.
- Non-positive quantities.
- Non-positive unit prices.
- VAT rates outside the inclusive `0..1` range.
- Values that cannot be converted to the required domain type.

Custom validation errors must provide actionable structured information:

- `row`: the input row index when applicable.
- `field`: the logical or physical field when applicable.
- `value`: the rejected value when safe to expose.
- `code`: a stable machine-readable error code.
- `message`: a human-readable explanation.

## 7. Package Structure

```text
shared_calculation/
├── api.py
├── models.py
├── validation.py
├── calculation.py
├── exceptions.py
├── adapters.py
└── tests/
    ├── test_validation.py
    └── test_calculation.py
```

Responsibilities must remain separated: `api.py` orchestrates, `validation.py` validates, `calculation.py` calculates, and `adapters.py` handles optional source-format concerns.

## 8. Testing Requirements

Automated tests must cover:

- A single valid line.
- Multiple lines and totals.
- VAT rates `0` and `1`.
- Multiple VAT rates.
- Duplicate item names without aggregation.
- Preservation of extra columns.
- Custom column mappings.
- Missing mappings and missing fields.
- Invalid item names, quantities, prices, and VAT rates.
- Two-decimal rounding and total calculation from rounded lines.
- Structured error attributes.

## 9. Definition of Done

The feature is complete when the public API works, all rules in this specification are implemented, Decimal arithmetic is used, original input is preserved, errors are actionable, automated tests pass, and the README documents installation and usage. No out-of-scope infrastructure is required.
