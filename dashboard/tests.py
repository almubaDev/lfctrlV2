from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from finances.models import AnnualFlow, MonthlyIncomeBook, Remnant


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='strong-password'
        )

    def test_finance_stats_are_dynamic(self):
        self.client.login(email='test@example.com', password='strong-password')

        flow_year = timezone.now().year
        flow = AnnualFlow.objects.create(year=flow_year)
        current_month = timezone.now().month
        monthly_book = MonthlyIncomeBook.objects.create(
            annual_flow=flow,
            month=current_month
        )
        Remnant.objects.create(
            income_book=monthly_book,
            amount=Decimal('150.50')
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        apps = response.context['apps']
        finance_app = next(app for app in apps if app['name'] == 'Control Financiero')

        self.assertEqual(
            finance_app['stats'][0],
            {'label': 'Flujos Anual', 'value': str(flow_year)}
        )
        remnant_value = finance_app['stats'][1]['value']
        self.assertTrue(remnant_value.startswith('$'))
        self.assertIn('150.50', remnant_value)
        self.assertEqual(finance_app['stats'][1]['label'], 'Remanentes')
