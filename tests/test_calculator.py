import unittest
from decimal import Decimal

from tax_calculation_library.calculator import calculate_line_tax, calculate_order_tax


class TaxCalculatorTests(unittest.TestCase):
    def test_calculate_line_tax(self) -> None:
        result = calculate_line_tax({"sku": "SKU1", "quantity": 3, "unit_price": "10.00"}, "0.10")

        self.assertEqual(result["line_subtotal"], Decimal("30.00"))
        self.assertEqual(result["line_tax"], Decimal("3.00"))
        self.assertEqual(result["line_total"], Decimal("33.00"))

    def test_calculate_line_tax_for_tax_exempt_item(self) -> None:
        result = calculate_line_tax(
            {"sku": "SKU1", "quantity": 3, "unit_price": "10.00", "tax_exempt": True}, "0.10"
        )

        self.assertEqual(result["line_tax"], Decimal("0.00"))
        self.assertEqual(result["line_total"], Decimal("30.00"))

    def test_calculate_order_tax(self) -> None:
        items = [
            {"sku": "SKU1", "quantity": 2, "unit_price": "10.00"},
            {"sku": "SKU2", "quantity": 1, "unit_price": "5.00", "tax_exempt": True},
        ]

        result = calculate_order_tax(items, "0.10")

        self.assertEqual(result["order_subtotal"], Decimal("25.00"))
        self.assertEqual(result["order_tax"], Decimal("2.00"))
        self.assertEqual(result["order_total"], Decimal("27.00"))


if __name__ == "__main__":
    unittest.main()
