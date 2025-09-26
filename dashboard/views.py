from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

@login_required
def dashboard_view(request):
    # Importar los modelos aquí para evitar problemas de importación circular
    try:
        from tracking.models import WeightRecord, BodyMeasurement, ProgressPhoto
        
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
        
    except:
        weight_stats = {'current': None, 'date': None}
        recent_measurements = 0
        recent_photos = 0
    
    apps = [
        {
            'name': 'Control Financiero',
            'description': 'Gestiona tus ingresos, gastos y presupuestos',
            'icon': 'fas fa-chart-line',
            'url': 'finances:flow-list',
            'color': 'bg-primary',
            'stats': [
                {'label': 'Flujos Anuales', 'value': '2024'},
                {'label': 'Balance', 'value': 'Positivo'},
            ]
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