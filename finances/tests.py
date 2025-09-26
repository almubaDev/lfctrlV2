from django.test import SimpleTestCase

from finances.templatetags.expense_filters import format_money


class FormatMoneyFilterTests(SimpleTestCase):
    def test_format_money_formats_thousands_with_dots(self):
        self.assertEqual(format_money(50000), "50.000")

    def test_format_money_invalid_values_return_zero(self):
        self.assertEqual(format_money("invalid"), "0")
        self.assertEqual(format_money(None), "0")
