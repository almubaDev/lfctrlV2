from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    # Weight tracking
    path('weight/', views.weight_tracker, name='weight_tracker'),
    path('weight/delete/<int:pk>/', views.weight_delete, name='weight_delete'),
    
    # Body measurements
    path('measurements/', views.measurements, name='measurements'),
    path('measurements/delete/<int:pk>/', views.measurement_delete, name='measurement_delete'),
    
    # Progress photos
    path('photos/', views.photos, name='photos'),
    path('photos/delete/<int:pk>/', views.photo_delete, name='photo_delete'),
    path('photos/compare/', views.photo_compare, name='photo_compare'),
    path('photos/date/', views.get_photos_for_date, name='get_photos_for_date'),
]