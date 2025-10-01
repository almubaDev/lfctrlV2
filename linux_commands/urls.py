from django.urls import path

from . import views

app_name = 'linux_commands'

urlpatterns = [
    path('', views.command_list, name='list'),
    path('create/', views.command_create, name='create'),
    path('<int:pk>/editar/', views.command_update, name='update'),
    path('<int:pk>/eliminar/', views.command_delete, name='delete'),
    path('tag-suggestions/', views.tag_suggestions, name='tag_suggestions'),
]
