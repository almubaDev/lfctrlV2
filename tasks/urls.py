from django.urls import path

from .views import task_complete, task_list

app_name = "tasks"

urlpatterns = [
    path("", task_list, name="today"),
    path("<int:pk>/complete/", task_complete, name="complete"),
]
