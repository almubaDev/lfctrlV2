from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_dashboard),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('finances/', include('finances.urls')),
    path('tracking/', include('tracking.urls')),  # Nueva app
    path('tasks/', include('tasks.urls')),
    path('linux-commands/', include('linux_commands.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)