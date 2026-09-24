import unittest
from decimal import Decimal

from tax_calculation_library.validation import validate_item_record


class ValidateItemRecordTests(unittest.TestCase):
    def test_valid_item_record(self) -> None:
        item = {"sku": " ABC123 ", "quantity": 2, "unit_price": "9.99", "tax_exempt": True}

        validated = validate_item_record(item)

        self.assertEqual(validated["sku"], "ABC123")
        self.assertEqual(validated["quantity"], 2)
        self.assertEqual(validated["unit_price"], Decimal("9.99"))
        self.assertTrue(validated["tax_exempt"])

    def test_missing_required_fields_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_item_record({"sku": "SKU1", "quantity": 1})

    def test_invalid_quantity_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate_item_record({"sku": "SKU1", "quantity": 0, "unit_price": "1.00"})

    def test_invalid_unit_price_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate_item_record({"sku": "SKU1", "quantity": 1, "unit_price": -1})


if __name__ == "__main__":
    unittest.main()
