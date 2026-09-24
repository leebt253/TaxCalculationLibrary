# Coding Rules: Tax Calculation Library

## General Principles

- Keep the project library-first, dependency-light, deterministic, and easy to test.
- Prefer the smallest change that satisfies the specification.
- Keep business rules explicit in the owning module.
- Do not introduce a database, web framework, UI, service layer, or unrelated infrastructure into V1.
- Use clear names and avoid one-letter variables.

## Architecture and Boundaries

- `api.py` owns the public API and orchestration.
- `models.py` owns result, item, metadata, and domain data models.
- `validation.py` owns metadata and input validation.
- `calculation.py` owns pure tax and total calculations.
- `exceptions.py` owns structured custom exceptions.
- `adapters.py` handles optional source-format conversion at the boundary.

The calculation core must not depend on CSV parsing, filesystem access, network calls, or persistence.

## Public API

- Keep `calculate(data, metadata)` as the primary public entry point.
- Do not add delimiter, encoding, physical file name, or rounding arguments to the calculation API.
- Treat metadata as the source of truth for physical column names.
- Keep public models and exception fields stable and documented.

## Types and Numeric Safety

- Use `decimal.Decimal` for VAT rates and all monetary arithmetic.
- Never use `float` for money, VAT, or intermediate values.
- Construct Decimal values from strings or validated integers, not binary floats.
- Use positive `int` values for `quantity` and `unit_price`.
- Treat VAT as a ratio: `Decimal("0.1")` represents 10%.
- Accept VAT only in the inclusive range `0..1`.
- Quantize monetary line values to `Decimal("0.01")` with `ROUND_HALF_UP` before summing totals.
- Keep calculation functions deterministic and free of hidden global state.

## Validation and Errors

- Validate required metadata before processing records.
- Validate every required field and never silently skip invalid records.
- Use fail-fast behavior for V1.
- Raise project-specific exceptions instead of leaking low-level conversion errors.
- Structured validation errors expose `row`, `field`, `value`, `code`, and `message` where applicable.
- Keep error codes stable and messages actionable without exposing secrets.

## Data and Calculation Behavior

- Preserve the complete original record, including unmapped extra columns.
- Calculate each input row independently.
- Never aggregate rows merely because item names or identifiers match.
- Sum totals from rounded line values.
- Keep the default currency as Korean Won (KRW) unless the specification changes.

## Testing and Documentation

- Add or update tests with every behavior change.
- Cover valid lines, multiple VAT rates, VAT `0` and `1`, duplicate items, mappings, extra fields, rounding, totals, and invalid inputs.
- Assert structured error attributes, not only exception text.
- Keep tests deterministic and independent of external services.
- Update `README.md` for user-visible behavior, `specification.md` for contract changes, and `recommendation.md` for architecture changes.
- Keep examples consistent with the implemented models.

## Review Checklist

- The change stays within its owning module.
- No float-based monetary arithmetic was introduced.
- Validation remains fail-fast and structured.
- Original data and extra columns remain intact.
- Duplicate rows remain independent.
- Rounding occurs at the documented point.
- Focused tests and then the full suite pass.
- Documentation and public API changes are synchronized.
