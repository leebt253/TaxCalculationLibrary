# Recommendation: Python Shared Calculation Library

## 1. Recommended Direction

Build a small, library-first Python package for tax calculation. The first version should focus on the calculation and validation core and expose one stable public entry point:

```python
calculate(data, metadata)
```

The core should accept normalized records and metadata. It must not depend on a database, web framework, UI, or a particular file format.

## 2. Scope for V1

### Include

- Metadata validation and logical-to-physical column mapping.
- Validation of required fields and value ranges.
- Per-line before-tax, VAT, and after-tax calculation.
- Order totals.
- Structured calculation results and validation errors.
- Preservation of every original input field.
- A minimal CSV adapter only after the core is complete.

### Exclude

- Database persistence.
- Web API or application workflow.
- Currency conversion.
- Advanced export features.
- Duplicate-item aggregation.
- Refunds, negative quantities, or negative prices.
- Business workflow and authorization.

## 3. Architecture

Use a small package with explicit responsibilities:

```text
shared_calculation/
├── api.py           # Public calculate() entry point
├── models.py        # Result, item, metadata, and error models
├── validation.py    # Metadata and input validation
├── calculation.py   # Decimal-based calculation rules
├── exceptions.py    # Structured custom exceptions
├── adapters.py      # Optional minimal CSV boundary
└── tests/
    ├── test_validation.py
    └── test_calculation.py
```

Keep adapters at the boundary. The calculation core should operate on records and metadata rather than parsing CSV details.

## 4. Delivery Order

1. Define models and metadata contract.
2. Implement validation and structured errors.
3. Implement Decimal calculation and rounding.
4. Expose `calculate(data, metadata)`.
5. Add focused automated tests.
6. Add the minimal CSV adapter if the core is complete and time remains.
7. Document installation, input shape, output shape, and examples.

## 5. Technical Decisions

- Target Python 3.x and keep the package dependency-light.
- Use `decimal.Decimal` for VAT rates and monetary arithmetic; never use `float` for money.
- Represent VAT as a ratio: `0.1` means 10%.
- Validate `quantity` and `unit_price` as positive integers.
- Validate `vat_rate` inclusively in the range `0..1`.
- Calculate each input row independently; never aggregate duplicate items.
- Quantize monetary line results to two decimal places before calculating totals.
- Use an explicit, documented Decimal rounding mode. V1 uses `ROUND_HALF_UP` unless a domain owner specifies another policy.
- Fail fast on invalid metadata or data. Do not silently skip invalid rows.
- Preserve all original fields, including unmapped extra columns.

## 6. Acceptance Checklist

- `calculate(data, metadata)` is importable and usable without infrastructure.
- Required column mappings and values are validated.
- Results contain line-level values and order totals.
- Original records and extra columns are preserved.
- Decimal arithmetic and two-decimal monetary output are enforced.
- Errors expose row, field, value, code, and message where applicable.
- Tests cover valid calculations, boundaries, rounding, mappings, preservation, and failures.
- README contains setup and a runnable example.
- No database, web server, or unnecessary framework is introduced.
