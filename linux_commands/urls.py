from django.urls import path

from . import views

app_name = 'linux_commands'

urlpatterns = [
    path('', views.command_list, name='list'),
    path('create/', views.command_create, name='create'),
    path('tag-suggestions/', views.tag_suggestions, name='tag_suggestions'),
]
