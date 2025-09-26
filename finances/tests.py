from unittest.mock import patch

from django.test import SimpleTestCase


from finances.templatetags.expense_filters import format_money


class FormatMoneyFilterTests(SimpleTestCase):
    def test_format_money_formats_thousands_with_dots(self):
        self.assertEqual(format_money(50000), "50.000")

    def test_format_money_invalid_values_return_zero(self):
        self.assertEqual(format_money("invalid"), "0")
        self.assertEqual(format_money(None), "0")


    @patch("finances.templatetags.expense_filters.number_format", return_value="50 000")
    def test_format_money_replaces_spaces_with_dots(self, mocked_number_format):
        self.assertEqual(format_money(50000), "50.000")
        mocked_number_format.assert_called_once()
