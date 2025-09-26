from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    apps = [
        {
            'name': 'Control Financiero',
            'description': 'Gestiona tus ingresos, gastos y presupuestos',
            'icon': 'fas fa-chart-line',
            'url': 'finances:flow-list',
            'color': 'bg-primary',
            'stats': [
                {'label': 'Flujos Anuales', 'value': ''},
                {'label': 'Finanzas', 'value': ''},
            ]
        },
        # Aquí se pueden agregar más apps en el futuro
    ]
    
    return render(request, 'dashboard/dashboard.html', {
        'apps': apps,
        'user': request.user
    })