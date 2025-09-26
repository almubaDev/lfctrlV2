from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_DOWN

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.formats import number_format

def format_currency(amount):
    try:
        if amount in (None, ""):
            return "$0"
        normalized = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_DOWN)
        formatted = number_format(
            normalized,
            decimal_pos=0,
            use_l10n=True,
            force_grouping=True,
        )
        return f"${formatted.replace(',', '.')}"
    except (TypeError, ValueError, InvalidOperation):
        return "$0"


@login_required
def dashboard_view(request):
    # Importar los modelos aquí para evitar problemas de importación circular
    try:
        from tracking.models import WeightRecord, BodyMeasurement, ProgressPhoto
        from finances.models import AnnualFlow

        # Obtener estadísticas de tracking
        latest_weight = WeightRecord.objects.filter(user=request.user).order_by('-date').first()
        weight_stats = {
            'current': latest_weight.weight if latest_weight else None,
            'date': latest_weight.date if latest_weight else None
        }

        # Contar registros del último mes
        last_month = datetime.now().date() - timedelta(days=30)
        recent_measurements = BodyMeasurement.objects.filter(
            user=request.user,
            date__gte=last_month
        ).count()
        recent_photos = ProgressPhoto.objects.filter(
            user=request.user,
            date__gte=last_month
        ).count()

        latest_finance_flow = AnnualFlow.objects.order_by('-year').first()
        current_flow_year = latest_finance_flow.year if latest_finance_flow else datetime.now().year
        accumulated_remnants = latest_finance_flow.get_accumulated_remnant() if latest_finance_flow else 0
        finance_stats = [
            {'label': 'Flujos Anual', 'value': str(current_flow_year)},
            {'label': 'Remanentes', 'value': format_currency(accumulated_remnants)},
        ]

    except Exception:
        weight_stats = {'current': None, 'date': None}
        recent_measurements = 0
        recent_photos = 0
        finance_stats = [
            {'label': 'Flujos Anual', 'value': str(datetime.now().year)},
            {'label': 'Remanentes', 'value': format_currency(0)},
        ]

    apps = [
        {
            'name': 'Control Financiero',
            'description': 'Gestiona tus ingresos, gastos y presupuestos',
            'icon': 'fas fa-chart-line',
            'url': 'finances:flow-list',
            'color': 'bg-primary',
            'stats': finance_stats
        },
        {
            'name': 'Seguimiento Físico',
            'description': 'Registra tu peso, medidas y progreso fotográfico',
            'icon': 'fas fa-heartbeat',
            'url': 'tracking:weight_tracker',
            'color': 'bg-danger',
            'stats': [
                {'label': 'Peso Actual', 'value': f"{weight_stats['current']:.1f} kg" if weight_stats['current'] else 'Sin datos'},
                {'label': 'Registros (30d)', 'value': f"{recent_measurements + recent_photos}"},
            ]
        },
    ]

    return render(request, 'dashboard/dashboard.html', {
        'apps': apps,
        'user': request.user
    })
